import cv2
import mediapipe as mp
import numpy as np
import math
import pyautogui
import screen_brightness_control as sbc
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
import logging
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import time 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize mouse controller
mouse = MouseController()

# Volume control initialization
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

class GestureController:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.is_running = False
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Screen dimensions
        screen_info = pyautogui.size()
        self.wscreen, self.hscreen = screen_info.width, screen_info.height
        self.wcam, self.hcam = 640, 480
        self.camera.set(3, self.wcam)
        self.camera.set(4, self.hcam)
        
        # Mouse control parameters
        self.frameR = 200
        self.smoothening = 7
        self.plocX, self.plocY = 0, 0
        
        # Finger tip IDs
        self.tipIds = [4, 8, 12, 16, 20]
        
    def run(self):
        """Main gesture control loop"""
        self.is_running = True
        pTime = time.time()  # Initialize with current time
        
        try:
            while self.is_running:
                success, frame = self.camera.read()
                if not success:
                    logger.warning("Failed to read camera frame")
                    continue
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process hand gestures
                hand_results = self.hands.process(rgb_frame)
                if hand_results.multi_hand_landmarks:
                    for handLms in hand_results.multi_hand_landmarks:
                        self.mp_draw.draw_landmarks(frame, handLms, mp.solutions.hands.HAND_CONNECTIONS)
                        self.process_gestures(frame, handLms)
                
                # Display FPS
                cTime = time.time()
                fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
                pTime = cTime
                cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                cv2.putText(frame, f"Press q to exit", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow("Gesture Control", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            logger.error(f"Error in gesture control loop: {str(e)}")
        finally:
            self.stop()
    
    def process_gestures(self, frame, hand_landmarks):
        """Process hand gestures"""
        try:
            lmList = []
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            
            if len(lmList) == 0:
                return
            
            # Get finger states
            fingers = []
            fingers.append(1 if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0]-1][1] else 0)
            for id in range(1, 5):
                fingers.append(1 if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id]-2][2] else 0)
            
            # Mouse movement
            if fingers == [0, 1, 0, 0, 0]:
                x1, y1 = lmList[8][1], lmList[8][2]
                cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                
                x3 = np.interp(x1, (self.frameR, self.wcam-self.frameR), (0, self.wscreen))
                y3 = np.interp(y1, (self.frameR, self.hcam-self.frameR), (0, self.hscreen))
                
                clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                clocY = self.plocY + (y3 - self.plocY) / self.smoothening
                
                # Ensure coordinates are within screen boundaries
                clocX = max(0, min(clocX, self.wscreen))
                clocY = max(0, min(clocY, self.hscreen))
                
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

                # Calculate length between fingers
                length = math.hypot(x2-x1, y2-y1)
                
                # Draw volume bar
                center_x1, center_y1 = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(frame, (center_x1, center_y1), 15, (255, 0, 0), cv2.FILLED)
                
                # Calculate volume percentage
                vol_percentage = np.interp(length, [30, 250], [0, 100])
                
                # Draw volume bar background
                bar_x = 50
                bar_y = 150 
                bar_width = 40
                bar_height = 200
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 0, 0), 3)
                
                # Draw filled volume bar
                fill_height = int(bar_height * (vol_percentage / 100))
                cv2.rectangle(frame, 
                            (bar_x, bar_y + bar_height - fill_height),
                            (bar_x + bar_width, bar_y + bar_height),
                            (255, 0, 0), cv2.FILLED)
                
                # Add volume percentage text
                cv2.putText(frame, f'{int(vol_percentage)}%', 
                          (bar_x, bar_y - 20),
                          cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                
                # Set volume
                vol = np.interp(length, [30, 250], [minVol, maxVol])
                volume.SetMasterVolumeLevel(vol, None)
            
            # Scroll
            elif fingers == [0, 1, 1, 1, 0]:
                x1, y1 = lmList[8][1], lmList[8][2]  # Fixed: Added x1 definition
                scroll_amount = np.interp(y1, [50, self.hcam-50], [-5, 5])
                mouse.scroll(0, int(scroll_amount))  # Cast to int for stability
                cv2.circle(frame, (x1, y1), 15, (255, 192, 203), cv2.FILLED)  # Fixed: Replaced "pink" with RGB
            
            # Brightness control
            elif fingers == [0, 0, 0, 0, 1]:
                x1, y1 = lmList[20][1], lmList[20][2]  # Using pinky finger (ID 20)
                brightness = np.interp(y1, [50, self.hcam-50], [0, 100])
                sbc.set_brightness(int(brightness))
                cv2.circle(frame, (x1, y1), 15, (0, 255, 255), cv2.FILLED)  # Fixed: Replaced "yellow" with RGB

                # Draw brightness bar
                bar_x = 50
                bar_y = 150 
                bar_width = 40
                bar_height = 200
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (0, 255, 255), 3)
                
                # Draw filled brightness bar
                fill_height = int(bar_height * (brightness / 100))  # Fixed: Using brightness instead of undefined vol_percentage
                cv2.rectangle(frame, 
                            (bar_x, bar_y + bar_height - fill_height),
                            (bar_x + bar_width, bar_y + bar_height),
                            (0, 255, 255), cv2.FILLED)
                
                # Add brightness percentage text
                cv2.putText(frame, f'{int(brightness)}%', 
                          (bar_x, bar_y - 20),
                          cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
        
        except Exception as e:
            logger.error(f"Error processing gestures: {str(e)}")
    
    def stop(self):
        """Cleanup resources"""
        self.is_running = False
        try:
            if self.camera.isOpened():
                self.camera.release()
            cv2.destroyAllWindows()
            self.hands.close()
        except Exception as e:
            logger.error(f"Error stopping gesture controller: {str(e)}")

# Main execution block
if __name__ == "__main__":
    controller = GestureController()
    controller.run()