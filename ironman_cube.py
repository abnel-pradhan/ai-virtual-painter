import cv2
import numpy as np
import mediapipe as mp
import math

print("\n" + "="*40)
print("🚀 STARTING IRONMAN CUBE MODE v2.0 🚀")
print("========================================")

# --- CONFIGURATION ---
COLOR_CYAN = (255, 255, 0)      # Ironman Blue
COLOR_RED = (0, 0, 255)         # Target/Move Color
COLOR_ERASER = (0, 0, 0)        # Black (Eraser)
CUBE_SIZE = 30                  # How big the 3D cubes are
BRUSH_THICKNESS = 50            # Eraser size

# 1. Initialize MediaPipe (Dual Hands Enabled)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.85)
mp_draw = mp.solutions.drawing_utils

# 2. Setup Camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# 3. Canvas Setup
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

# Variables for drawing
xp, yp = 0, 0

def draw_3d_cube(img, center, size, color):
    """Draws a cool 3D Cube at the given center point"""
    x, y = center
    half = size // 2
    depth = size // 3  # How "deep" the 3D look is

    # Define the Front Face
    front_face = np.array([
        [x - half, y - half], # Top Left
        [x + half, y - half], # Top Right
        [x + half, y + half], # Bottom Right
        [x - half, y + half]  # Bottom Left
    ], np.int32)

    # Define the Back Face (Shifted for 3D effect)
    back_face = np.array([
        [x - half + depth, y - half - depth],
        [x + half + depth, y - half - depth],
        [x + half + depth, y + half - depth],
        [x - half + depth, y + half - depth]
    ], np.int32)

    # Draw Connections (Lines between front and back)
    for i in range(4):
        cv2.line(img, tuple(front_face[i]), tuple(back_face[i]), color, 2)

    # Draw Front and Back Faces
    cv2.polylines(img, [back_face], True, color, 1)
    cv2.polylines(img, [front_face], True, color, 2)
    
    # Fill the Front Face slightly for a "Solid" look
    overlay = img.copy()
    cv2.fillPoly(overlay, [front_face], color)
    cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)

while True:
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1) # Mirror

    # Find Hands
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            
            # --- VISUALS: Draw Robotic Connections ---
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS,
                                   mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=2, circle_radius=4),
                                   mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=2))

            # Get Landmarks
            lmList = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if len(lmList) != 0:
                # Key Points
                x1, y1 = lmList[8][1:]   # Index Tip
                x2, y2 = lmList[12][1:]  # Middle Tip
                
                # Check Fingers (Up = 1, Down = 0)
                fingers = []
                # Thumb (Simplified check)
                if lmList[4][1] > lmList[3][1]: fingers.append(1)
                else: fingers.append(0)
                # 4 Fingers
                for id in [8, 12, 16, 20]:
                    if lmList[id][2] < lmList[id - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # ---------------- MODES ----------------

                # 1. ERASER MODE (All 5 Fingers Up)
                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                    xp, yp = 0, 0
                    cv2.circle(img, (x1, y1), 50, COLOR_RED, 2)
                    cv2.putText(img, "ERASER ACTIVE", (x1, y1-60), cv2.FONT_HERSHEY_PLAIN, 2, COLOR_RED, 2)
                    # Erase on canvas
                    cv2.circle(imgCanvas, (x1, y1), BRUSH_THICKNESS, (0, 0, 0), cv2.FILLED)

                # 2. SELECTION/MOVE MODE (Index + Middle Up)
                elif fingers[1] == 1 and fingers[2] == 1:
                    xp, yp = 0, 0
                    cv2.rectangle(img, (x1-20, y1-20), (x2+20, y2+20), COLOR_RED, 2)
                    cv2.putText(img, "MOVE CURSOR", (x1, y1-30), cv2.FONT_HERSHEY_PLAIN, 1, COLOR_RED, 2)

                # 3. DRAWING MODE (Only Index Up)
                elif fingers[1] == 1 and fingers[2] == 0:
                    
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1
                    
                    # Interpolation: Draw cubes between points to avoid gaps
                    distance = math.hypot(x1 - xp, y1 - yp)
                    steps = int(distance / 10) + 1  # Draw a cube every 10 pixels
                    
                    for i in range(steps):
                        inter_x = int(xp + (x1 - xp) * i / steps)
                        inter_y = int(yp + (y1 - yp) * i / steps)
                        
                        # Draw Cube on Canvas
                        draw_3d_cube(imgCanvas, (inter_x, inter_y), CUBE_SIZE, COLOR_CYAN)

                    xp, yp = x1, y1
                
                else:
                    xp, yp = 0, 0 # Reset if other gestures

    # Merge Canvas
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 10, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    cv2.imshow("Ironman Cube V2", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break