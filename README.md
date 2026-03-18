# 🦸‍♂️ Ironman 3D Virtual Painter

An AI-powered, futuristic Heads-Up Display (HUD) that lets you draw 3D blocks in the air using hand gestures. Built with Python, OpenCV, and Google's MediaPipe.

## ✨ Features
* **Ironman HUD**: Custom cyan skeletal tracking with a futuristic interface.
* **3D Cube Brush**: Instead of flat lines, draw hollow 3D cubes with solid front faces.
* **Smart Grid System**: Cubes snap to an invisible grid, preventing messy overlapping.
* **Gesture Controls**: Draw, move, and erase seamlessly using natural hand movements.
* **Dual-Hand Support**: Use your left, right, or both hands simultaneously!

## 🛠️ Tech Stack
* **Python** (Recommended: v3.10)
* **OpenCV** (cv2) - For webcam and image processing
* **MediaPipe** - For real-time hand landmark detection
* **NumPy** - For canvas generation and matrix math

---

## 🚀 Installation & Setup

Because newer versions of MediaPipe have removed certain modules, **you must use the exact versions listed below** to prevent errors.

**1. Clone or Download this repository**
```bash
git clone [https://github.com/yourusername/ironman-virtual-painter.git](https://github.com/yourusername/ironman-virtual-painter.git)
cd ironman-virtual-painter
```

**2. Create a Virtual Environment (Highly Recommended)**
```bash
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate

# On Mac/Linux:
source .venv/bin/activate
```

**3. Install the Required Dependencies**
Run this exact command to avoid version conflicts (specifically `AttributeError: module 'mediapipe' has no attribute 'solutions'`):
```bash
pip install "mediapipe==0.10.14" "protobuf>=4.25.3,<5" "numpy<2" opencv-python
```

---

## 🎮 How to Use (Controls)

Run the script from your terminal:
```bash
python ironman_cube.py
```

Once the camera window opens, use the following gestures:

* 🟦 **Draw (Index Finger Only):** Raise just your index finger to place 3D cubes.
* 🟥 **Move/Hover (Index + Middle Fingers):** Raise two fingers to move your hand around the screen *without* drawing.
* ⚫ **Eraser (All 5 Fingers):** Open your entire hand (like a high-five) to activate a massive eraser.
* ❌ **Quit:** Press the **'q'** key on your keyboard to close the application safely.

---

## ⚠️ Troubleshooting

* **`cv2.error: !_src.empty()`**: This means your camera isn't turning on. 
  * Check if another app (Zoom, Teams, Discord) is using your webcam.
  * If you have multiple cameras, open the code and change `cap = cv2.VideoCapture(0)` to `cap = cv2.VideoCapture(1)`.
* **`ModuleNotFoundError`**: Your virtual environment isn't activated. Make sure you see `(.venv)` in your terminal before running the script.

## 🤝 Contributing
Feel free to fork this project, submit pull requests, or send suggestions!
