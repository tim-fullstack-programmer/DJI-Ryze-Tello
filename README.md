# Custom software for the DJI Ryze Tello drone – v1.0.0

> Custom desktop software for the **DJI Ryze Tello** drone. Built with **Python** & **PyQt5**, featuring offline **Russian voice control**, **AI face-tracking**, real-time telemetry, and a threaded responsive GUI.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/PyQt5-GUI-green?logo=qt" />
  <img src="https://img.shields.io/badge/VosK-Russian_ Speech-orange" />
  <img src="https://img.shields.io/badge/MediaPipe-Face_Tracking-purple" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Voice Control** | Offline Russian speech recognition via **VosK** (10+ commands) |
| 🖱️ **PyQt5 GUI** | Live video feed, battery & altitude telemetry, emoji buttons |
| ⌨️ **Keyboard Piloting** | Instant hotkeys for all flight maneuvers |
| 👤 **AI Follow-me** | **MediaPipe** face detection + **PID** auto-centering & distance hold |
| 📷 **Photo Capture** | One-click snapshot from drone camera |
| 📡 **Live Telemetry** | Real-time battery % and flight height readouts |
| ⚡ **Multi-threaded** | Voice, keyboard, GUI & video stream run in parallel without blocking |
| 🎨 **Bright Design** | Colorful accessible interface with built-in help dialog |

---

## Getting Started

### Prerequisites
- Python **3.8+**
- Wi-Fi adapter (connect to `TELLO-XXXXXX` network)
- Microphone (for voice control)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/username/tello-ai-controller.git
cd tello-ai-controller

# 2. Install dependencies
pip install djitellopy pyqt5 opencv-python numpy mediapipe vosk pyaudio keyboard
```

### Model Download
Download the **VosK Russian model** [`vosk-model-small-ru-0.4`](https://alphacephei.com/vosk/models) and extract it into the project root.

---

## Usage

### 1️⃣ Connect
Power on the drone, connect your PC to its Wi-Fi network, and run:
```bash
python main.py
```

### 2️⃣ Take off
Click **🛫 Takeoff** in the GUI, press `F`, or say **"взлёт"**.

### 3️⃣ Pilot
- **GUI buttons** – directional controls with emoji-labeled buttons.
- **Voice** – speak Russian commands (вперёд, назад, влево, вправо, вверх, вниз, посадка).
- **Keyboard** – `W/A/S/D` to move, `Shift/Ctrl` for altitude, `Q/E` to rotate.

### 4️⃣ AI Follow-me
Press `U` (or trigger via GUI) to activate **face-tracking mode**. The drone autonomously centers your face and maintains distance using PID control. Press **Landing** or `Space` to exit and land.

### 5️⃣ Photo & Telemetry
- Click **⚪** or press `P` to capture a snapshot (`frame_qimg*.png`).
- Monitor **Battery** and **Altitude** readouts at the top of the window.

---

## Voice Commands (Russian)

| Command | Action |
|---------|--------|
| `взлёт` | Takeoff |
| `посадка` | Land |
| `вперёд` | Move forward |
| `назад` | Move backward |
| `влево` / `лево` | Move left |
| `вправо` / `право` | Move right |
| `вверх` / `верх` | Move up |
| `вниз` / `низ` | Move down |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `F` | Takeoff |
| `Space` | Land |
| `W` / `S` | Forward / Back |
| `A` / `D` | Left / Right |
| `Shift` | Up |
| `Ctrl` | Down |
| `Q` / `E` | Rotate CCW / CW |
| `P` | Take photo |
| `U` | Toggle AI Follow-me |

---

## Project Structure

```
tello-ai-controller/
├── main.py              # Main app: GUI + voice + keyboard + video
├── follow.py            # Standalone AI face-tracking script
├── utils/
│   └── PlotModule.py    # Real-time PID plot visualizer
├── vosk-model-small-ru-0.4/  # Speech recognition model
└── frame_qimg*.png      # Saved snapshots
```

---

## Tech Stack

- [`djitellopy`](https://github.com/damiafuentes/DJITelloPy) – Tello SDK
- [`PyQt5`](https://www.riverbankcomputing.com/software/pyqt/) – Desktop GUI
- [`VosK`](https://github.com/alphacep/vosk-api) – Offline speech-to-text
- [`MediaPipe`](https://mediapipe.dev/) – Face detection
- [`OpenCV`](https://opencv.org/) – Video processing
- [`NumPy`](https://numpy.org/) – PID mathematics

---

## License

This project is open-source. Feel free to modify, extend, and integrate with your own drone setups.

---

<p align="center"><b>⭐ Star this repo if it helped your Tello take flight!</b></p>
