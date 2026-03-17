import cv2
import numpy as np
import mediapipe as mp
import math

print("\n" + "="*40)
print("🚀 STARTING IRONMAN BLOCKS MODE 🚀")
print("===================================")

# --- CONFIGURATION ---
COLOR_CYAN = (255, 255, 0)      # Ironman Blue
COLOR_RED = (0, 0, 255)         # Target/Move Color
COLOR_ERASER = (0, 0, 0)        # Black

# CRITICAL SETTINGS FOR "SINGLE BOX" FEEL
CUBE_SIZE = 40                  # Size of the box
GAP_SIZE = 45                   # MINIMUM distance to move before drawing next box
                                # (Set GAP_SIZE > CUBE_SIZE to see spaces between them)

# 1. Initialize MediaPipe
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
    """Draws a single 3D Cube"""
    x, y = center
    half = size // 2
    depth = size // 4  # Depth of the 3D effect

    # Front Face
    front_face = np.array([
        [x - half, y - half], [x + half, y - half],
        [x + half, y + half], [x - half, y + half]
    ], np.int32)

    # Back Face
    back_face = np.array([
        [x - half + depth, y - half - depth], [x + half + depth, y - half - depth],
        [x + half + depth, y + half - depth], [x - half + depth, y + half - depth]
    ], np.int32)

    # Draw Edges (Connections)
    for i in range(4):
        cv2.line(img, tuple(front_face[i]), tuple(back_face[i]), color, 2)

    # Draw Faces (Hollow style for cool look)
    cv2.polylines(img, [back_face], True, color, 1)
    cv2.polylines(img, [front_face], True, color, 3)
    
    # Fill slightly to block what's behind it
    cv2.fillPoly(img, [front_face], (0, 0, 0)) # Black out behind front face
    cv2.polylines(img, [front_face], True, color, 3) # Redraw outline

while True:
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)

    # Find Hands
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            
            # Draw Hand Skeleton
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS,
                                   mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=1, circle_radius=2),
                                   mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=1))

            lmList = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]   # Index Tip
                x2, y2 = lmList[12][1:]  # Middle Tip
                
                # Check Fingers
                fingers = []
                # Thumb
                if lmList[4][1] > lmList[3][1]: fingers.append(1)
                else: fingers.append(0)
                # 4 Fingers
                for id in [8, 12, 16, 20]:
                    if lmList[id][2] < lmList[id - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                # ---------------- MODES ----------------

                # 1. ERASER (Open Hand - All 5 fingers)
                if fingers.count(1) == 5:
                    xp, yp = 0, 0 # Reset anchor
                    cv2.circle(img, (x1, y1), 60, COLOR_RED, 2)
                    cv2.putText(img, "ERASING", (x1, y1-70), cv2.FONT_HERSHEY_PLAIN, 2, COLOR_RED, 2)
                    cv2.circle(imgCanvas, (x1, y1), 60, (0,0,0), cv2.FILLED)

                # 2. MOVE (Index + Middle)
                elif fingers[1] == 1 and fingers[2] == 1:
                    xp, yp = 0, 0 # Reset anchor
                    cv2.rectangle(img, (x1-20, y1-20), (x2+20, y2+20), COLOR_RED, 2)
                    cv2.putText(img, "MOVE", (x1, y1-30), cv2.FONT_HERSHEY_PLAIN, 2, COLOR_RED, 2)

                # 3. DRAW SINGLE BOXES (Index Only)
                elif fingers[1] == 1 and fingers[2] == 0:
                    
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1 # Set start point
                    
                    # --- SPACING LOGIC ---
                    # Calculate how far finger moved from last box
                    distance = math.hypot(x1 - xp, y1 - yp)
                    
                    # Only draw if we moved enough (GAP_SIZE)
                    if distance > GAP_SIZE:
                        
                        # Calculate exactly where to put cubes along the path
                        # so they are evenly spaced
                        num_boxes = int(distance / GAP_SIZE)
                        
                        for i in range(1, num_boxes + 1):
                            # Interpolate position
                            ratio = i / num_boxes
                            new_x = int(xp + (x1 - xp) * ratio)
                            new_y = int(yp + (y1 - yp) * ratio)
                            
                            # Draw ONE solid cube here
                            draw_3d_cube(imgCanvas, (new_x, new_y), CUBE_SIZE, COLOR_CYAN)
                        
                        # Update the "Last Drawn" position to the current finger tip
                        xp, yp = x1, y1
                
                else:
                    xp, yp = 0, 0

    # Merge Canvas
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 10, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    cv2.imshow("Ironman Blocks", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break