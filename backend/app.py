from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import os
import logging
from gesture_controller import GestureController
import speech_recognition as sr
import webbrowser
import pyttsx3

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize voice engine
voice_engine = pyttsx3.init()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for system state
gesture_controller = None
gesture_thread = None
is_gesture_active = False
is_voice_active = False
system_lock = threading.Lock()

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
                gesture_controller = GestureController()
                gesture_thread = threading.Thread(target=gesture_controller.run, daemon=True)
                gesture_thread.start()
                is_gesture_active = True
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
    
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400
    
    enable = data.get('enable', False)
    is_voice_active = enable
    
    return jsonify({
        "status": "success",
        "message": f"Voice control {'activated' if enable else 'deactivated'}",
        "isActive": is_voice_active
    })

def process_voice_command(command):
    try:
        command = command.lower()
        if 'open youtube' in command:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube"
        elif 'open google' in command:
            webbrowser.open("https://google.com")
            return "Opening Google"
        # Add more commands as needed
        else:
            return f"I didn't understand: {command}"
    except Exception as e:
        logger.error(f"Command processing error: {str(e)}")
        return "Sorry, I encountered an error"

@app.route('/api/process_command', methods=['POST'])
def handle_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"status": "error", "message": "Missing command"}), 400
    
    response = process_voice_command(data['command'])
    voice_engine.say(response)
    voice_engine.runAndWait()
    
    return jsonify({
        "status": "success",
        "message": response,
        "command": data['command']
    })


@app.route('/api/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"status": "error", "message": "Missing command"}), 400
    
    # Process the command here (you'll need to implement this)
    # For example:
    # response = process_voice_command(data['command'])
    
    return jsonify({
        "status": "success",
        "message": "Command received",
        "command": data['command']
    })

@app.route('/api/system_status', methods=['GET'])
def system_status():
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
        app.run(host='0.0.0.0', port=6000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        if gesture_controller:
            gesture_controller.stop()
        if gesture_thread:
            gesture_thread.join(timeout=1)