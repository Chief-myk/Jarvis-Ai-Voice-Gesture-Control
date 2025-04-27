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
import random
from datetime import datetime
import pyjokes
import openai
import os


os.environ['FLASK_NO_COLOR'] = '1' 
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define story elements for random story generation
characters = ["wizard", "knight", "dragon", "scientist", "explorer", "astronaut"]
locations = ["magical forest", "ancient castle", "futuristic city", "underwater kingdom", "desert oasis"]
activities = ["find a hidden treasure", "solve an ancient mystery", "rescue a lost friend", "discover a new species", "build a fantastic machine"]

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
voice_thread = None
system_lock = threading.Lock()

def cleanup_resources():
    """Clean up all resources on exit"""
    global gesture_controller, gesture_thread, is_gesture_active, voice_thread
    
    logger.info("Cleaning up resources...")
    if gesture_controller:
        try:
            gesture_controller.stop()
        except Exception as e:
            logger.error(f"Error stopping gesture controller: {str(e)}")
    
    if gesture_thread and gesture_thread.is_alive():
        gesture_thread.join(timeout=1)
    
    # Stop voice listening thread
    global is_voice_active
    is_voice_active = False
    if voice_thread and voice_thread.is_alive():
        voice_thread.join(timeout=1)
    
    if voice_engine:
        try:
            voice_engine.engine.stop() if voice_engine.engine else None
        except Exception as e:
            logger.error(f"Error stopping voice engine: {str(e)}")

atexit.register(cleanup_resources)

# Helper function for gesture control toggling (internal use)
def toggle_gestures_internal(enable):
    global is_gesture_active, gesture_controller, gesture_thread
    
    with system_lock:
        if enable and not is_gesture_active:
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
            return True
        elif not enable and is_gesture_active:
            if gesture_controller:
                gesture_controller.stop()
            if gesture_thread:
                gesture_thread.join(timeout=1)
            is_gesture_active = False
            return True
    return False

# def generate_response(command):
#     """Generate a response using OpenAI API with better error handling"""
#     # Get API key from environment variable
#     openai_api_key = os.getenv("OPENAI_API_KEY")
    
#     if not openai_api_key:
#         return "I can't answer that right now because my AI connection is not configured."
    
#     try:
#         # Create a system message that guides the AI to give concise responses
#         system_message = """You are a helpful voice assistant providing brief, concise responses.
#         Keep responses under 50 words when possible. Be friendly but efficient."""
        
#         # Updated OpenAI API call for newer client versions
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": command}
#             ],
#             max_tokens=125,
#             temperature=0.7,
#             timeout=5  # 5 second timeout
#         )
#         return response.choices[0].message.content.strip()
#     except openai.APITimeoutError:
#         return "I'm sorry, the request timed out. Please try again."
#     except openai.RateLimitError:
#         return "I've reached my request limit. Please try again in a moment."
#     except openai.APIConnectionError:
#         return "I'm having trouble connecting to my knowledge base. Please check your internet connection."
#     except Exception as e:
#         logger.error(f"Error generating AI response: {str(e)}")
#         return "I encountered an error while processing your request."

def process_voice_command(command):
    """Process voice command with enhanced functionality and error handling"""
    global is_voice_active
    
    try:
        command = command.lower().strip()
        
        # Exit commands
        exit_words = ["exit", "bye", "goodbye", "quit", "stop", "shut up", "keep quiet"]
        if any(exit_word in command for exit_word in exit_words):
            is_voice_active = False
            return "Voice control deactivated. Signing off!"
        
        # Web browsing commands
        if 'open youtube' in command:
            webbrowser.open("https://youtube.com")
            return "Opening YouTube"
        elif 'open google' in command:
            webbrowser.open("https://google.com")
            return "Opening Google"
        elif 'open gmail' in command:
            webbrowser.open("https://mail.google.com")
            return "Opening Gmail"
        elif 'open maps' in command:
            webbrowser.open("https://maps.google.com")
            return "Opening Google Maps"
        elif 'play music' in command:
            webbrowser.open("https://music.youtube.com")
            return "Opening YouTube Music"
        elif 'open spotify' in command:
            webbrowser.open("https://open.spotify.com")
            return "Opening Spotify"
        
        # Time and date information
        elif any(word in command for word in ['time', 'clock']):
            current_time = datetime.now().strftime('%I:%M %p')
            return f"The current time is {current_time}"
        elif any(word in command for word in ['date', 'day', 'today']):
            current_date = datetime.now().strftime('%A, %B %d, %Y')
            return f"Today is {current_date}"
        
        # Entertainment commands
        elif 'tell me a story' in command:
            return f"Once upon a time, there was a {random.choice(characters)} who lived in a {random.choice(locations)}. One day, they went on an adventure to {random.choice(activities)} and had a lot of fun!"
        elif 'tell me a joke' in command or 'make me laugh' in command:
            return pyjokes.get_joke()
        elif 'play a random song' in command:
            song_urls = [
                "https://www.youtube.com/watch?v=lt8ZIrNEUL8",
                "https://www.youtube.com/watch?v=8of5w7RgcTc",
                "https://www.youtube.com/watch?v=Fk0ySAL1dLs",
                "https://www.youtube.com/watch?v=0MxVtp3Up1k",
                "https://www.youtube.com/watch?v=gpKxohYVFH8"
            ]
            webbrowser.open(random.choice(song_urls))
            return "Playing a random song for you."
        elif 'play a random video' in command:
            video_urls = [
                "https://www.youtube.com/watch?v=3pCDMXuurVM",
                "https://www.youtube.com/watch?v=0fYi8SGA20k",
                "https://www.youtube.com/watch?v=Gj75E31JYe4",
                "https://www.youtube.com/watch?v=2C6omXxIcyE",
                "https://www.youtube.com/watch?v=Ji8yCh8VcRo",
                "https://www.youtube.com/watch?v=lI16LeQV9Js"
            ]
            webbrowser.open(random.choice(video_urls))
            return "Playing a random video for you."
        
        # System control commands
        elif 'activate gesture control' in command or 'turn on gestures' in command:
            # Toggle gesture control on
            toggle_gestures_internal(True)
            return "Gesture control activated"
        elif 'deactivate gesture control' in command or 'turn off gestures' in command:
            # Toggle gesture control off
            toggle_gestures_internal(False)
            return "Gesture control deactivated"
        
        # Weather placeholder - would integrate with actual weather API
        elif 'what is the weather today' in command:
            location = command.split('weather in')[-1].strip() if 'weather in' in command else "your area"
            return f"The weather in {location} is sunny with a temperature of 72 degrees Fahrenheit."
        
        # AI assistance command
        # elif any(phrase in command for phrase in ["ask ai", "ask gpt", "ask chat"]):
        #     # Extract the question part after the command phrase
        #     for phrase in ["ask ai", "ask gpt", "ask chat"]:
        #         if phrase in command:
        #             question = command.split(phrase, 1)[1].strip()
        #             break
        #     else:
        #         question = ""
                
        #     if question:
        #         return generate_response(question)
        #     else:
        #         return "What would you like to ask me?"
        
        # Help command
        elif 'help' in command or 'what can you do' in command:
            return "I can open websites, tell jokes, play music, control gestures, tell stories, check time and date, or answer questions. Just ask me what you need!"
        
        # Unknown command
        else:
            # Try to generate a response for unknown commands
            # if len(command) > 3:  # Only for non-trivial input
                # return generate_response(command)
            return f"I didn't understand: {command}. Say 'help' for a list of commands."
            
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}")
        return "Sorry, I encountered an error while processing your request."
        

def voice_listener():
    """Function that continuously listens for voice commands"""
    global is_voice_active
    
    logger.info("Starting voice listener thread")
    voice_engine.speak("Voice control is now active")
    
    while is_voice_active:
        try:
            with sr.Microphone() as source:
                logger.info("Listening for commands...")
                voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = voice_recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                try:
                    command = voice_recognizer.recognize_google(audio).lower()
                    logger.info(f"Recognized: {command}")
                    
                    # Process the command
                    response = process_voice_command(command)
                    voice_engine.speak(response)
                    
                    # Check if we need to exit the loop
                    if any(exit_word in command for exit_word in ["exit", "bye", "goodbye", "quit", "stop"]):
                        break
                    
                except sr.UnknownValueError:
                    logger.info("Could not understand audio")
                except sr.RequestError as e:
                    logger.error(f"Google Speech Recognition service error: {e}")
                except Exception as e:
                    logger.error(f"Voice recognition error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Microphone error: {str(e)}")
            time.sleep(1)  # Prevent CPU spike on repeated errors
    
    logger.info("Voice listener thread stopped")

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
    global is_voice_active, voice_thread
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Missing JSON payload"}), 400

        enable = data.get('enable', False)
        
        with system_lock:
            # If turning voice control on and it's not currently active
            if enable and not is_voice_active:
                is_voice_active = True
                # Start voice listener in a separate thread
                voice_thread = threading.Thread(target=voice_listener, daemon=True)
                voice_thread.start()
                response_msg = "Voice control activated"
            # If turning voice control off and it is currently active
            elif not enable and is_voice_active:
                is_voice_active = False
                # The voice_listener thread will stop on its own in the next loop
                if voice_thread and voice_thread.is_alive():
                    voice_thread.join(timeout=1)
                response_msg = "Voice control deactivated"
            else:
                response_msg = "No change to voice control"
                
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
        response = process_voice_command(command)
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
        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize voice recognizer with sensitivity settings
        voice_recognizer.energy_threshold = 300
        voice_recognizer.dynamic_energy_threshold = True
        voice_recognizer.pause_threshold = 0.8
        
        # Start with minimal configuration first
        app.run(host='127.0.0.1', port=5001, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}, {type(e)}")
        import traceback
        logger.error(traceback.format_exc())
        cleanup_resources()