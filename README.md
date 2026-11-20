# ISHARA
### AI-Powered Hand Gesture Control System

**Software Engineering • Computer Vision • Human-Computer Interaction**

ISHARA is a Windows desktop application that enables hands-free computer interaction through real-time hand tracking and gesture recognition.

Built with Python, OpenCV, MediaPipe, and PyAutoGUI, ISHARA translates hand movements into desktop actions, offering an alternative way to navigate and control a computer using a webcam.

---

## Overview

ISHARA explores the intersection of **Software Engineering, Artificial Intelligence, and Human-Computer Interaction (HCI)**.

The application integrates a pretrained hand-landmark detection model with custom gesture interpretation and desktop automation logic, creating a real-time interaction system.

The project focuses on building a functional desktop application through software integration, interface development, gesture-based interaction, testing, and Windows deployment.

## Key Features

- **Real-Time Hand Tracking:** Detects and tracks hand landmarks through a webcam.
- **Cursor Control:** Moves the mouse pointer using index-finger movements.
- **Mouse Actions:** Supports left-clicking, right-clicking, and scrolling through hand gestures.
- **Presentation Mode:** Navigates presentation slides without touching the keyboard.
- **Gesture-Based Mode Switching:** Switches between mouse and presentation control using an open-palm gesture.
- **Interactive Interface:** Displays tracking status, active mode, and on-screen controls.
- **Windows Application:** Packaged as a desktop executable for Windows.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Application development and control logic |
| OpenCV | Webcam capture and interface rendering |
| MediaPipe | Hand landmark detection |
| PyAutoGUI | Mouse and keyboard automation |
| PyInstaller | Windows executable packaging |

## Software Engineering

ISHARA demonstrates practical software engineering concepts, including:

- Integration of computer vision and desktop automation components
- Real-time video processing and gesture interpretation
- State-based interaction and application mode management
- User interface development
- Debugging and functional testing
- Desktop application packaging and distribution

## How It Works

1. The webcam captures live video frames.
2. MediaPipe identifies hand landmarks.
3. The application interprets landmark positions and gesture patterns.
4. Recognized gestures are mapped to mouse or presentation commands.
5. The interface provides visual feedback during interaction.

## Gesture Controls

| Gesture | Action |
|---|---|
| Move index finger | Move cursor |
| Thumb and index finger pinch | Left click |
| Thumb and middle finger pinch | Right click |
| Index and middle fingers | Scroll in Mouse Mode |
| Open palm (hold) | Switch control mode |
| Index finger raised | Next slide in Presentation Mode |
| Index and middle fingers raised | Previous slide in Presentation Mode |
| Closed fist (hold) | Return to Mouse Mode |

## Installation

### Run from Source

Requirements:
- Windows
- Python 3.12
- Working webcam

Clone the repository:

```bash
git clone https://github.com/Ghala77-prog/ISHARA.git
cd ISHARA
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

### Windows Application

A packaged Windows version will be available through the GitHub Releases section.

The application requires a webcam and may require Windows camera permissions.

## Screenshots and Demo

Application screenshots and a demonstration video will be added to showcase hand tracking, mouse interaction, and presentation controls.

## Project Scope

ISHARA uses a pretrained MediaPipe model for hand landmark detection. Gesture interpretation, interaction logic, interface integration, and desktop control are implemented at the application level.

The project is intended as a practical demonstration of software engineering, computer vision integration, and gesture-based human-computer interaction.

## Developer

**Ghala Alharbi**

Data Science Graduate | Software Engineering & AI Projects

[Portfolio](https://ghala77-prog.github.io/ghala-portfolio/) | [GitHub](https://github.com/Ghala77-prog)

---

**ISHARA — Control your computer with a gesture.**

