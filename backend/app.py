from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import logging
from gesture_controller import GestureController
import webbrowser
import pyttsx3
import speech_recognition as sr
import traceback
import os
import time
import atexit
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Thread-safe Voice Engine
class VoiceEngine:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.engine = None
                    cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        try:
            self.engine = pyttsx3.init(driverName='sapi5')  # Force sapi5 on Windows
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 1.0)
        except Exception as e:
            logger.error(f"Voice engine init failed: {str(e)}")
            self.engine = None
    
    def speak(self, text):
        if not self.engine:
            logger.warning("Voice engine not available")
            return
            
        try:
            # Stop any current speech
            self.engine.stop()
            # Say the new text
            self.engine.say(text)
            # Run without wait to prevent blocking
            self.engine.startLoop(False)
            # Start a new thread for running the loop
            t = threading.Thread(target=self.engine.iterate)
            t.daemon = True
            t.start()
        except RuntimeError:
            try:
                self.engine.endLoop()
                self.speak(text)
            except Exception as e:
                logger.error(f"Speech error: {str(e)}")

voice_engine = VoiceEngine()
voice_recognizer = sr.Recognizer()

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Global variables for system state
gesture_controller = None
gesture_thread = None
is_gesture_active = False
is_voice_active = False
system_lock = threading.Lock()

def cleanup_resources():
    """Clean up all resources on exit"""
    global gesture_controller, gesture_thread, is_gesture_active
    
    logger.info("Cleaning up resources...")
    if gesture_controller:
        try:
            gesture_controller.stop()
        except Exception as e:
            logger.error(f"Error stopping gesture controller: {str(e)}")
    
    if gesture_thread and gesture_thread.is_alive():
        gesture_thread.join(timeout=1)
    
    if voice_engine:
        try:
            voice_engine.engine.stop() if voice_engine.engine else None
        except Exception as e:
            logger.error(f"Error stopping voice engine: {str(e)}")

atexit.register(cleanup_resources)

@app.route('/api/toggle_gestures', methods=['POST'])
def toggle_gestures():
    global is_gesture_active, gesture_controller, gesture_thread

    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

    enable = data.get('enable', False)

    with system_lock:
        if enable and not is_gesture_active:
            try:
                # Clean up any existing instances
                if gesture_controller:
                    gesture_controller.stop()
                if gesture_thread:
                    gesture_thread.join(timeout=1)
                
                # Create new instances
                gesture_controller = GestureController()
                gesture_thread = threading.Thread(target=gesture_controller.run, daemon=True)
                gesture_thread.start()
                is_gesture_active = True
                voice_engine.speak("Gesture control activated")
                return jsonify({
                    "status": "success",
                    "message": "Gesture control activated",
                    "isActive": True
                })
            except Exception as e:
                logger.error(f"Gesture start error: {str(e)}")
                return jsonify({"status": "error", "message": str(e)}), 500

        elif not enable and is_gesture_active:
            try:
                if gesture_controller:
                    gesture_controller.stop()
                if gesture_thread:
                    gesture_thread.join(timeout=1)
                is_gesture_active = False
                voice_engine.speak("Gesture control deactivated")
                return jsonify({
                    "status": "success",
                    "message": "Gesture control deactivated",
                    "isActive": False
                })
            except Exception as e:
                logger.error(f"Gesture stop error: {str(e)}")
                return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({
        "status": "success",
        "message": "No change",
        "isActive": is_gesture_active
    })

@app.route('/api/toggle_voice', methods=['POST'])
def toggle_voice():
    global is_voice_active
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

        enable = data.get('enable', False)
        is_voice_active = enable
        
        response_msg = f"Voice control {'activated' if enable else 'deactivated'}"
        voice_engine.speak(response_msg)
        
        return jsonify({
            "status": "success",
            "message": response_msg,
            "isActive": is_voice_active
        })
    except Exception as e:
        logger.error(f"Voice toggle error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "stackTrace": traceback.format_exc()
        }), 500

@app.route('/api/process_command', methods=['POST'])
def handle_command():
    """Handle incoming voice commands"""
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"status": "error", "message": "Missing command"}), 400
    
    command = data['command'].lower()
    print(f"Received command: {command}")  # Debug log
    
    try:
        if 'open youtube' in command:
            webbrowser.open("https://youtube.com")
            response = "Opening YouTube"
        elif 'open google' in command:
            webbrowser.open("https://google.com")
            response = "Opening Google"
        elif 'play music' in command:
            webbrowser.open("https://music.youtube.com")
            response = "Opening YouTube Music"
        elif 'what time is it' in command:
            response = f"The current time is {datetime.now().strftime('%H:%M')}"
        else:
            response = f"I didn't understand: {command}"
            
        logger.info(f"Processed command: {command} -> {response}")
        voice_engine.speak(response)
        
        return jsonify({
            "status": "success",
            "message": response,
            "command": command
        })
        
    except Exception as e:
        logger.error(f"Command processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Command processing failed",
            "error": str(e)
        }), 500

@app.route('/api/system_status', methods=['GET'])
def system_status():
    """Get current system status"""
    camera_open = False
    if gesture_controller and hasattr(gesture_controller, 'camera'):
        try:
            camera_open = gesture_controller.camera.isOpened()
        except:
            camera_open = False

    return jsonify({
        "gestureActive": is_gesture_active,
        "voiceActive": is_voice_active,
        "cameraStatus": camera_open
    })

if __name__ == '__main__':
    try:
        # Disable reloader to prevent duplicate threads
        app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        cleanup_resources()