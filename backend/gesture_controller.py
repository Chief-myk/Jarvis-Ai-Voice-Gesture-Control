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
import wolframalpha  # For computational queries
from plyer import notification  # For desktop notifications
import keyboard  # For hotkey detection
from translate import Translator  # For real-time translation
import pytz  # For timezone handling
from geopy.geocoders import Nominatim  # For location detection
import screen_brightness_control as sbc  # For brightness control
from pynput.mouse import Controller as MouseController  # For precise mouse control
from pynput.keyboard import Controller as KeyboardController  # For keypress simulation
from pynput.mouse import Button 

# ====================== INITIALIZATION ======================
# Suppress warnings
warnings.filterwarnings("ignore")

# Initialize system components
engine = pyttsx3.init()
recognizer = sr.Recognizer()
command_queue = Queue()  # Thread-safe command queue
mouse = MouseController()
kb = KeyboardController()

# Screen dimensions for mouse control
screen_info = screeninfo.get_monitors()[0]
wscreen, hscreen = screen_info.width, screen_info.height

# Camera setup
cap = cv2.VideoCapture(0)
wcam, hcam = 1240, 680
cap.set(3, wcam)
cap.set(4, hcam)

# Mouse control parameters
frameR = 200  # Frame reduction for mouse movement area
smoothening = 7
plocX, plocY = 0, 0  # Previous location
clocX, clocY = 0, 0  # Current location

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

# # Face recognition setup
# people = ['Mayank Mittal', 'Siddhi Sharma']
# haar_cascade = cv2.CascadeClassifier(q'haar_face.xml')
# face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# # Load trained face recognition model if exists
# model_path = "face_trained.yml"
# if os.path.exists(model_path):
#     face_recognizer.read(model_path)


# Finger tip IDs (for hand landmarks)
tipIds = [4, 8, 12, 16, 20]

# # AI Clients
# openai_client = OpenAI(api_key="your-openai-key")  # Replace with your key
# wolfram_client = wolframalpha.Client("your-wolfram-alpha-key")  # For computational queries

# ====================== UTILITY FUNCTIONS ======================
def speak(text, rate=150):
    """Improved text-to-speech with rate control"""
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def listen(timeout=5):
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
        
def play_random_song():
    """Play a random song from predefined list"""
    songs = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=JGwWNGJdvx8",
        "https://www.youtube.com/watch?v=9bZkp7q19f0"
    ]
    speak("Playing music")
    webbrowser.open(random.choice(songs))

def set_volume(change):
    """Adjust volume by percentage change"""
    current = volume.GetMasterVolumeLevelScalar() * 100
    new_vol = max(0, min(100, current + change))
    volume.SetMasterVolumeLevelScalar(new_vol/100, None)
    speak(f"Volume set to {int(new_vol)}%")        



def process_command(command):
    """Process and execute user commands"""
    print("Executing command:", command)
    
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
        "record screen": lambda: record_screen(10)
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

def process_voice_command(command=None):
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
        print(f"Voice command error: {e}")

def execute_task(task):
    """Execute a predefined automation task"""
    if task == "morning_routine":
        speak("Starting your morning routine.")
        webbrowser.open("https://www.google.com")
        time.sleep(2)
        pyautogui.hotkey('win', 'd')  # Show desktop
        time.sleep(1)
        os.startfile("outlook")  # Open Outlook
    elif task == "work_mode":
        speak("Activating work mode.")
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE")  # Open Word
        os.startfile("C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE")  # Open Excel
    elif task == "shutdown_pc":
        speak("Shutting down the system in 1 minute.")
        os.system("shutdown /s /t 60")

def get_weather(city="auto"):
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
    except:
        speak("Could not fetch weather data.")

def set_brightness(level):
    """Set screen brightness (0-100)"""
    sbc.set_brightness(level)
    speak(f"Screen brightness set to {level}%")

def take_screenshot():
    """Take and save a screenshot"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    pyautogui.screenshot(filename)
    speak(f"Screenshot saved as {filename}")

def record_screen(duration=10):
    """Record screen for given duration (seconds)"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.mp4"
    speak(f"Recording screen for {duration} seconds")
    
    # Requires ffmpeg
    subprocess.run(f"ffmpeg -f gdigrab -i desktop -t {duration} {filename}", shell=True)
    speak(f"Screen recording saved as {filename}")

def translate_text(text, target_lang="hi"):
    """Translate text to target language"""
    translator = Translator(to_lang=target_lang)
    translation = translator.translate(text)
    speak(f"Translation: {translation}")
    return translation

def detect_emotion(face_image):
    """Simple emotion detection from facial features"""
    # This is a placeholder - in practice, use a trained ML model
    return "neutral"

def lock_system():
    """Lock the computer"""
    ctypes.windll.user32.LockWorkStation()
    speak("System locked")

def send_notification(title, message):
    """Send desktop notification"""
    notification.notify(
        title=title,
        message=message,
        app_name="JARVIS",
        timeout=10
    )

# ====================== AI INTEGRATION ======================
# def ai_chat(query):
#     """Get AI response using OpenAI"""
#     try:
#         response = openai_client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are JARVIS, an AI assistant. Be concise and helpful."},
#                 {"role": "user", "content": query}
#             ],
#             temperature=0.7
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"AI error: {e}")
#         return "I encountered an error processing your request."

# def wolfram_query(query):
#     """Answer computational queries using Wolfram Alpha"""
#     try:
#         res = wolfram_client.query(query)
#         return next(res.results).text
#     except:
#         return "I couldn't compute that."

# ====================== GESTURE CONTROL ======================
# def recognize_face(frame):
#     """Recognize faces in the frame with enhanced detection"""
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = haar_cascade.detectMultiScale(gray, 1.1, 4)
    
#     for (x, y, w, h) in faces:
#         face_roi = gray[y:y+h, x:x+w]
        
#         try:
#             label, confidence = face_recognizer.predict(face_roi)
#             name = people[label] if confidence < 70 else "Unknown"
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#             cv2.putText(frame, f"{name} ({confidence:.1f})", (x, y-10), 
#                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#             return name
#         except:
#             return "Unknown"
    
#     return None

def process_gestures(frame, hand_landmarks):
    """Enhanced gesture processing with more controls"""
    global plocX, plocY
    
    lmList = []
    for id, lm in enumerate(hand_landmarks.landmark):
        h, w, c = frame.shape
        cx, cy = int(lm.x * w), int(lm.y * h)
        lmList.append([id, cx, cy])
    
    if len(lmList) == 0:
        return
    
    # Get finger states
    fingers = []
    # Thumb
    fingers.append(1 if lmList[tipIds[0]][1] > lmList[tipIds[0]-1][1] else 0)
    # Other fingers
    for id in range(1, 5):
        fingers.append(1 if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2] else 0)
    
    # Mouse movement - only index finger up
    if fingers == [0, 1, 0, 0, 0]:
        x1, y1 = lmList[8][1], lmList[8][2]
        cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        
        # Convert coordinates to screen size
        x3 = np.interp(x1, (frameR, wcam-frameR), (0, wscreen))
        y3 = np.interp(y1, (frameR, hcam-frameR), (0, hscreen))
        
        # Smooth movement
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening
        
        # Move mouse
        mouse.position = (clocX, clocY)
        plocX, plocY = clocX, clocY
    
    # Left click - fist (all fingers down)
    elif sum(fingers) == 0:
        mouse.click(Button.left)
        cv2.putText(frame, "CLICK", (lmList[8][1], lmList[8][2]-30), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    
    # Right click - thumb and index up
    elif fingers == [1, 0, 0, 0, 0]:
        mouse.click(Button.right)
        cv2.putText(frame, "RIGHT CLICK", (lmList[8][1], lmList[8][2]-30), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    # Volume control - index and middle fingers up
    elif fingers == [0, 1, 1, 0, 0]:
        x1, y1 = lmList[8][1], lmList[8][2]
        x2, y2 = lmList[12][1], lmList[12][2]
        cv2.circle(frame, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(frame, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
        
        length = math.hypot(x2-x1, y2-y1)
        vol = np.interp(length, [30, 250], [minVol, maxVol])
        
        # Visual feedback
        vol_bar = np.interp(length, [30, 250], [400, 150])
        cv2.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(frame, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
        
        volume.SetMasterVolumeLevel(vol, None)
    
    # Scroll - index, middle, and ring fingers up
    elif fingers == [0, 1, 1, 1, 0]:
        y1 = lmList[8][2]
        scroll_amount = np.interp(y1, [50, hcam-50], [-5, 5])
        mouse.scroll(0, scroll_amount)
        cv2.putText(frame, f"SCROLL: {scroll_amount:.1f}", (50, 50), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
    
    # Brightness control - all fingers up
    elif fingers == [0, 0, 0, 0, 1]:
        x1, y1 = lmList[8][1], lmList[8][2]
        brightness = np.interp(y1, [50, hcam-50], [0, 100])
        set_brightness(int(brightness))
        cv2.putText(frame, f"BRIGHTNESS: {int(brightness)}%", (50, 50), 
                   cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

# ====================== MAIN LOOP ======================
def main():
    # Start voice processing thread
    voice_thread = threading.Thread(target=process_voice_command, daemon=True)
    voice_thread.start()
    
    pTime = 0
    active_mode = "voice"  # Can be "voice" or "gesture"
    # last_face_recognition = 0
    
    speak("System initialized. Hello sir, I am JARVIS. How may I assist you today?")
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hand gestures
        hand_results = hands.process(rgb_frame)
        if hand_results.multi_hand_landmarks:
            for handLms in hand_results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
                process_gestures(frame, handLms)
        
        # # Face recognition (every 2 seconds to reduce processing load)
        # current_time = time.time()
        # if current_time - last_face_recognition > 2:
        #     recognized_name = recognize_face(frame)
        #     if recognized_name and recognized_name != "Mayank Mittal":
        #         speak("Unauthorized user detected. System locked.")
        #         lock_system()
        #     last_face_recognition = current_time
        
        # Process voice commands from queue
        if not command_queue.empty():
            command = command_queue.get()
            process_voice_command(command)  # Now properly handles the argument
        
        # Display FPS and status
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        cv2.putText(frame, f"FPS: {int(fps)} | Mode: {active_mode.upper()}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        cv2.imshow("JARVIS Control System", frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()