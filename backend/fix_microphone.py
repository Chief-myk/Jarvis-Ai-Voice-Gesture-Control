import ctypes
import sys
import time
import winsound
import pythoncom
from pycaw.pycaw import AudioUtilities

def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        # Re-run with admin rights if not elevated
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False
    except:
        return False

def check_microphone():
    try:
        pythoncom.CoInitialize()
        devices = AudioUtilities.GetMicrophone()
        if devices:
            # print("✅ Microphone detected successfully!")
            winsound.Beep(1000, 500)  # High beep for success
            time.sleep(1)  # Keep window open
            return True
        else:
            # print("❌ No microphone detected!")
            winsound.Beep(200, 1000)  # Low beep for error
            time.sleep(3)  # Keep window open longer for error
            return False
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        winsound.Beep(200, 1500)  # Long low beep for critical error
        time.sleep(3)
        return False

if __name__ == "__main__":
    if run_as_admin():
        print("=== Microphone Checker ===")
        check_microphone()
        input("Press Enter to close...")  # Keeps window open
    else:
        print("Please run as Administrator!")
        time.sleep(3)