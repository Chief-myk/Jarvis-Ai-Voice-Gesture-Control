# Project Title:
JARVIS: AI Voice & Gesture Control

# Project Summary:
In an era where touchless interfaces are becoming increasingly essential, this project presents an innovative solution that enables users to control core laptop functionalities—such as mouse movement, clicking, scrolling, and volume adjustments—purely through hand gestures. This system leverages computer vision and web technologies to build a seamless and intuitive gesture-controlled environment, reducing dependency on physical input devices.

At the core of this project lies a real-time hand gesture recognition system, built using Python, OpenCV, and MediaPipe. It captures and analyzes hand movements via a webcam and maps them to specific computer actions using libraries like PyAutoGUI. Whether it’s increasing the volume with a simple hand motion, scrolling through a webpage with a swipe, or moving the cursor with your fingers—users gain full control over their system without touching it.

The project also includes a user-friendly web interface, developed using HTML, CSS, and JavaScript, which contains buttons to enable or disable gesture control. This interface communicates with a Flask backend, which starts or stops the Python gesture controller accordingly. This approach gives users the flexibility to activate gesture mode only when required, improving efficiency and system performance.

# Impact and Real-Life Applications:

🔹 Touchless Interaction: Highly relevant in hygienic environments (e.g., hospitals, labs) where physical contact with devices needs to be minimized.

🔹 Accessibility: Empowers people with limited mobility to interact with computers more easily.

🔹 Presentations & Smart Homes: Can be used during presentations to switch slides or control devices without a remote.

🔹 Modern UX/UI Integration: Showcases the future of human-computer interaction using AI and CV.

🔹 Customizability: Easy to expand and train for custom gestures and new functionalities.

# Key Technologies Used:

Python – Core programming language

OpenCV & MediaPipe – Real-time hand tracking and gesture recognition

PyAutoGUI – To control mouse, keyboard, and system volume

Flask – Lightweight Python web server to connect frontend with backend

HTML, CSS, JavaScript – To create a responsive website UI for gesture control toggling

# Unique Features:

🔁 Real-time gesture recognition using just a webcam

🎛️ Full system control without physical input (mouse, keyboard, etc.)

🌐 Interactive website toggle with live backend integration

🧠 Modular structure for easy upgrade and integration with voice or IoT systems

🧩 Easily expandable for additional gestures, face recognition, or smart assistant behavior

