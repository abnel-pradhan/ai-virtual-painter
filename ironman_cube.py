import cv2
import numpy as np
import mediapipe as mp
import math

print("\n" + "="*40)
print("🚀 STARTING IRONMAN GRID MODE 🚀")
print("===================================")

# --- CONFIGURATION ---
COLOR_CYAN = (255, 255, 0)      # Ironman Blue
COLOR_RED = (0, 0, 255)         # Target/Move Color
CUBE_SIZE = 50                  # Size of the grid cells

# NEW: Memory to remember exactly where we already printed blocks!
drawn_blocks = set()

# 1. Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.85)
mp_draw = mp.solutions.drawing_utils

# 2. Setup Camera
cap = cv2.VideoCapture(0) # Change to 1 if your camera doesn't turn on!
cap.set(3, 1280)
cap.set(4, 720)

# 3. Canvas Setup
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

def draw_3d_cube(img, center, size, color):
    """Draws a hollow 3D cube with solid front face"""
    x, y = center
    half = size // 2
    depth = size // 4
    
    front = np.array([[x-half, y-half], [x+half, y-half], [x+half, y+half], [x-half, y+half]], np.int32)
    back = np.array([[x-half+depth, y-half-depth], [x+half+depth, y-half-depth], [x+half+depth, y+half-depth], [x-half+depth, y+half-depth]], np.int32)

    for i in range(4):
        cv2.line(img, tuple(front[i]), tuple(back[i]), color, 2)
    cv2.polylines(img, [back], True, color, 1)
    cv2.fillPoly(img, [front], (0,0,0)) # Hides lines behind the cube
    cv2.polylines(img, [front], True, color, 3)

while True:
    success, img = cap.read()
    
    # --- CAMERA CRASH FIX ---
    if not success:
        print("⚠️ Camera is empty or blocked by another app (like Zoom).")
        break
        
    img = cv2.flip(img, 1)

    # Find Hands
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS, 
                                   mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=2, circle_radius=4),
                                   mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=2))
            
            lmList = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                lmList.append([id, int(lm.x * w), int(lm.y * h)])

            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]   # Index
                x2, y2 = lmList[12][1:]  # Middle
                
                fingers = []
                if lmList[4][1] > lmList[3][1]: fingers.append(1) # Thumb
                else: fingers.append(0)
                for id in [8, 12, 16, 20]:
                    if lmList[id][2] < lmList[id - 2][2]: fingers.append(1)
                    else: fingers.append(0)

                # 1. ERASER (All 5 Fingers)
                if fingers.count(1) == 5:
                    cv2.circle(img, (x1, y1), 60, COLOR_RED, 2)
                    cv2.putText(img, "ERASER", (x1, y1-70), cv2.FONT_HERSHEY_PLAIN, 2, COLOR_RED, 2)
                    cv2.circle(imgCanvas, (x1, y1), 60, (0,0,0), cv2.FILLED)
                    
                    # Also erase them from our Memory!
                    blocks_to_remove = set()
                    for (bx, by) in drawn_blocks:
                        if math.hypot(bx - x1, by - y1) < 60:
                            blocks_to_remove.add((bx, by))
                    drawn_blocks -= blocks_to_remove

                # 2. DRAW BLOCKS (Index Only)
                elif fingers[1] == 1 and fingers[2] == 0:
                    
                    # --- THE GRID MAGIC ---
                    # Force the coordinates to "snap" to a 50x50 invisible grid
                    grid_x = (x1 // CUBE_SIZE) * CUBE_SIZE + (CUBE_SIZE // 2)
                    grid_y = (y1 // CUBE_SIZE) * CUBE_SIZE + (CUBE_SIZE // 2)
                    
                    # Check if this grid spot is empty
                    if (grid_x, grid_y) not in drawn_blocks:
                        draw_3d_cube(imgCanvas, (grid_x, grid_y), CUBE_SIZE, COLOR_CYAN)
                        drawn_blocks.add((grid_x, grid_y)) # Save to memory so it never prints twice!

                # 3. MOVE (Index + Middle)
                elif fingers[1] == 1 and fingers[2] == 1:
                    cv2.rectangle(img, (x1-20, y1-20), (x2+20, y2+20), COLOR_RED, 2)
                    cv2.putText(img, "MOVE", (x1, y1-30), cv2.FONT_HERSHEY_PLAIN, 2, COLOR_RED, 2)

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 10, 255, cv2.THRESH_BINARY_INV)
    img = cv2.bitwise_or(cv2.bitwise_and(img, cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)), imgCanvas)

    cv2.imshow("Ironman Grid Mode", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break