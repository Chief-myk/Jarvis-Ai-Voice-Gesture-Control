import cv2
import mediapipe as mp
import time
import numpy as np
import speech_recognition as sr
import pyttsx3
import webbrowser
import random
import requests
import os
import math
import autopy
import pyautogui
import ctypes 
import threading 
from queue import Queue
import json
import screeninfo
import warnings
from openai import OpenAI
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import datetime
import subprocess
import pygetwindow as gw
from bs4 import BeautifulSoup
import wolframalpha
from plyer import notification
import keyboard
from translate import Translator
import pytz
from geopy.geocoders import Nominatim
import screen_brightness_control as sbc
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from typing import Dict, Any, Optional, List, Tuple

# ====================== INITIALIZATION ======================
warnings.filterwarnings("ignore")

# Initialize Flask app
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# System components
engine = pyttsx3.init()
recognizer = sr.Recognizer()
command_queue = Queue()
mouse = MouseController()
kb = KeyboardController()

# Screen dimensions
screen_info = screeninfo.get_monitors()[0]
wscreen, hscreen = screen_info.width, screen_info.height

# Camera setup
cap = cv2.VideoCapture(0)
wcam, hcam = 1240, 680
cap.set(3, wcam)
cap.set(4, hcam)

# Mouse control parameters
frameR = 200
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# MediaPipe solutions
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, 
                                 min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Finger tip IDs
tipIds = [4, 8, 12, 16, 20]

# System state
is_gesture_active = False
is_voice_active = False
system_lock = threading.Lock()

# ====================== GESTURE CONTROLLER CLASS ======================
class GestureController:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.is_running = False
        self.hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.plocX, self.plocY = 0, 0
        self.smoothening = 7
        self.frameR = 200
        self.wscreen, self.hscreen = screeninfo.get_monitors()[0].width, screeninfo.get_monitors()[0].height
        self.wcam, self.hcam = 1240, 680
        self.camera.set(3, self.wcam)
        self.camera.set(4, self.hcam)
        
    def run(self):
        """Main gesture control loop"""
        self.is_running = True
        pTime = 0
        
        while self.is_running:
            success, frame = self.camera.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand gestures
            hand_results = self.hands.process(rgb_frame)
            if hand_results.multi_hand_landmarks:
                for handLms in hand_results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
                    self.process_gestures(frame, handLms)
            
            # Display FPS
            cTime = time.time()
            fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
            pTime = cTime
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow("Gesture Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.camera.release()
        cv2.destroyAllWindows()
    
    def process_gestures(self, frame, hand_landmarks):
        """Process hand gestures"""
        lmList = []
        for id, lm in enumerate(hand_landmarks.landmark):
            h, w, c = frame.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
        
        if len(lmList) == 0:
            return
        
        # Get finger states
        fingers = []
        fingers.append(1 if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1] else 0)
        for id in range(1, 5):
            fingers.append(1 if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2] else 0)
        
        # Mouse movement
        if fingers == [0, 1, 0, 0, 0]:
            x1, y1 = lmList[8][1], lmList[8][2]
            cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            
            x3 = np.interp(x1, (self.frameR, self.wcam-self.frameR), (0, self.wscreen))
            y3 = np.interp(y1, (self.frameR, self.hcam-self.frameR), (0, self.hscreen))
            
            clocX = self.plocX + (x3 - self.plocX) / self.smoothening
            clocY = self.plocY + (y3 - self.plocY) / self.smoothening
            
            mouse.position = (clocX, clocY)
            self.plocX, self.plocY = clocX, clocY
        
        # Left click
        elif sum(fingers) == 0:
            mouse.click(Button.left)
            cv2.putText(frame, "CLICK", (lmList[8][1], lmList[8][2]-30), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        
        # Right click
        elif fingers == [1, 0, 0, 0, 0]:
            mouse.click(Button.right)
            cv2.putText(frame, "RIGHT CLICK", (lmList[8][1], lmList[8][2]-30), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        
        # Volume control
        elif fingers == [0, 1, 1, 0, 0]:
            x1, y1 = lmList[8][1], lmList[8][2]
            x2, y2 = lmList[12][1], lmList[12][2]
            cv2.circle(frame, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
            
            length = math.hypot(x2-x1, y2-y1)
            vol = np.interp(length, [30, 250], [minVol, maxVol])
            
            vol_bar = np.interp(length, [30, 250], [400, 150])
            cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
            cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
            
            volume.SetMasterVolumeLevel(vol, None)
        
        # Scroll
        elif fingers == [0, 1, 1, 1, 0]:
            y1 = lmList[8][2]
            scroll_amount = np.interp(y1, [50, self.hcam-50], [-5, 5])
            mouse.scroll(0, scroll_amount)
            cv2.putText(frame, f"SCROLL: {scroll_amount:.1f}", (50, 50), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
        
        # Brightness control
        elif fingers == [0, 0, 0, 0, 1]:
            x1, y1 = lmList[8][1], lmList[8][2]
            brightness = np.interp(y1, [50, self.hcam-50], [0, 100])
            set_brightness(int(brightness))
            cv2.putText(frame, f"BRIGHTNESS: {int(brightness)}%", (50, 50), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
    
    def stop(self):
        """Cleanup resources"""
        self.is_running = False
        self.camera.release()
        cv2.destroyAllWindows()

# Initialize gesture controller
gesture_controller = GestureController()

# ====================== UTILITY FUNCTIONS ======================
def speak(text: str, rate: int = 150) -> None:
    """Improved text-to-speech with rate control"""
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def listen(timeout: int = 5) -> str:
    """Enhanced speech recognition with noise cancellation"""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            print("Heard:", command)
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return ""

def play_random_song() -> None:
    """Play a random song from predefined list"""
    songs = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=JGwWNGJdvx8",
        "https://www.youtube.com/watch?v=9bZkp7q19f0"
    ]
    speak("Playing music")
    webbrowser.open(random.choice(songs))

def set_volume(change: int) -> None:
    """Adjust volume by percentage change"""
    current = volume.GetMasterVolumeLevelScalar() * 100
    new_vol = max(0, min(100, current + change))
    volume.SetMasterVolumeLevelScalar(new_vol/100, None)
    speak(f"Volume set to {int(new_vol)}%")

def get_weather(city: str = "auto") -> None:
    """Fetch weather data"""
    if city == "auto":
        geolocator = Nominatim(user_agent="jarvis-weather")
        location = geolocator.geocode("")
        city = location.address.split(',')[0]
    
    try:
        api_key = "your-weather-api-key"  # Replace with OpenWeatherMap API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        speak(f"Weather in {city}: {weather}, Temperature: {temp}°C, Humidity: {humidity}%")
    except Exception as e:
        logging.error(f"Weather fetch error: {e}")
        speak("Could not fetch weather data.")

def set_brightness(level: int) -> None:
    """Set screen brightness (0-100)"""
    sbc.set_brightness(level)
    speak(f"Screen brightness set to {level}%")

def take_screenshot() -> None:
    """Take and save a screenshot"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    pyautogui.screenshot(filename)
    speak(f"Screenshot saved as {filename}")

def record_screen(duration: int = 10) -> None:
    """Record screen for given duration (seconds)"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.mp4"
    speak(f"Recording screen for {duration} seconds")
    
    try:
        subprocess.run(f"ffmpeg -f gdigrab -i desktop -t {duration} {filename}", shell=True)
        speak(f"Screen recording saved as {filename}")
    except Exception as e:
        logging.error(f"Screen recording failed: {e}")
        speak("Failed to record screen")

def translate_text(text: str, target_lang: str = "hi") -> str:
    """Translate text to target language"""
    translator = Translator(to_lang=target_lang)
    translation = translator.translate(text)
    speak(f"Translation: {translation}")
    return translation

def lock_system() -> None:
    """Lock the computer"""
    ctypes.windll.user32.LockWorkStation()
    speak("System locked")

def send_notification(title: str, message: str) -> None:
    """Send desktop notification"""
    notification.notify(
        title=title,
        message=message,
        app_name="JARVIS",
        timeout=10
    )

def execute_task(task: str) -> None:
    """Execute a predefined automation task"""
    if task == "morning_routine":
        speak("Starting your morning routine.")
        webbrowser.open("https://www.google.com")
        time.sleep(2)
        pyautogui.hotkey('win', 'd')
        time.sleep(1)
        os.startfile("outlook")
    elif task == "work_mode":
        speak("Activating work mode.")
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")
    elif task == "shutdown_pc":
        speak("Shutting down the system in 1 minute.")
        os.system("shutdown /s /t 60")

# ====================== COMMAND PROCESSING ======================
def process_command(command: str) -> None:
    """Process and execute user commands"""
    logging.info(f"Executing command: {command}")
    
    command_map = {
        "open google": ("Opening Google", "https://www.google.com"),
        "open youtube": ("Opening YouTube", "https://www.youtube.com"),
        "open whatsapp": ("Opening WhatsApp", "https://web.whatsapp.com"),
        "open facebook": ("Opening Facebook", "https://www.facebook.com"),
        "open instagram": ("Opening Instagram", "https://www.instagram.com"),
        "play music": play_random_song,
        "what's the weather": get_weather,
        "take screenshot": take_screenshot,
        "lock computer": lock_system,
        "volume up": lambda: set_volume(10),
        "volume down": lambda: set_volume(-10),
        "mute": lambda: volume.SetMute(1, None),
        "unmute": lambda: volume.SetMute(0, None),
        "record screen": lambda: record_screen(10),
        "morning routine": lambda: execute_task("morning_routine"),
        "work mode": lambda: execute_task("work_mode"),
        "shutdown": lambda: execute_task("shutdown_pc"),
        "translate": lambda: translate_text(" ".join(command.split()[1:]))
    }
    
    if command.lower() in command_map:
        action = command_map[command.lower()]
        if callable(action):
            action()
        else:
            speak(action[0])
            webbrowser.open(action[1])
    else:
        response = ai_chat(command)
        speak(response)

def process_voice_command(command: Optional[str] = None) -> None:
    """Handle voice commands from mic or direct input"""
    try:
        if command is None:
            while True:
                command = listen()
                if command and "jarvis" in command.lower():
                    speak("Yes sir, how can I help?")
                    command = command.replace("jarvis", "").strip()
                    process_command(command)
        else:
            if "jarvis" in command.lower():
                speak("Yes sir, how can I help?")
                command = command.replace("jarvis", "").strip()
            process_command(command)
    except Exception as e:
        logging.error(f"Voice command error: {e}")

# ====================== AI INTEGRATION ======================
def ai_chat(query: str) -> str:
    """Placeholder AI response"""
    return "This feature requires an API key to be configured."

# ====================== FLASK API ENDPOINTS ======================
@app.route('/api/toggle_gestures', methods=['POST'])
def toggle_gestures():
    global is_gesture_active, gesture_controller
    
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Missing JSON payload"}), 400
    
    enable = data.get('enable', False)
    
    with system_lock:
        if enable and not is_gesture_active:
            try:
                gesture_thread = threading.Thread(target=gesture_controller.run, daemon=True)
                gesture_thread.start()
                is_gesture_active = True
                return jsonify({
                    "status": "success",
                    "message": "Gesture control activated",
                    "isActive": True
                })
            except Exception as e:
                logging.error(f"Gesture start error: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        elif not enable and is_gesture_active:
            try:
                gesture_controller.stop()
                is_gesture_active = False
                return jsonify({
                    "status": "success",
                    "message": "Gesture control deactivated",
                    "isActive": False
                })
            except Exception as e:
                logging.error(f"Gesture stop error: {e}")
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
    
    with system_lock:
        if enable and not is_voice_active:
            try:
                voice_thread = threading.Thread(target=process_voice_command, daemon=True)
                voice_thread.start()
                is_voice_active = True
                return jsonify({
                    "status": "success",
                    "message": "Voice control activated",
                    "isActive": True
                })
            except Exception as e:
                logging.error(f"Voice start error: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        
        elif not enable and is_voice_active:
            try:
                is_voice_active = False
                return jsonify({
                    "status": "success",
                    "message": "Voice control deactivated",
                    "isActive": False
                })
            except Exception as e:
                logging.error(f"Voice stop error: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({
        "status": "success",
        "message": "No change",
        "isActive": is_voice_active
    })

@app.route('/api/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"status": "error", "message": "Missing command"}), 400
    
    command = data['command']
    command_queue.put(command)
    
    return jsonify({
        "status": "success",
        "message": "Command queued for execution"
    })

@app.route('/api/system_status', methods=['GET'])
def system_status():
    camera_open = False
    if gesture_controller and gesture_controller.camera:
        try:
            camera_open = gesture_controller.camera.isOpened()
        except:
            camera_open = False
    
    return jsonify({
        "gestureActive": is_gesture_active,
        "voiceActive": is_voice_active,
        "cameraStatus": camera_open
    })

# ====================== MAIN EXECUTION ======================
def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Start the main JARVIS system
    speak("System initialized. Hello sir, I am JARVIS. How may I assist you today?")
    
    try:
        while True:
            # Process commands from queue
            if not command_queue.empty():
                command = command_queue.get()
                process_voice_command(command)
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Shutting down JARVIS system")
        gesture_controller.stop()
        cap.release()
        cv2.destroyAllWindows()