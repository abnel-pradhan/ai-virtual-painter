import cv2
import numpy as np
import mediapipe as mp

print("\n" + "="*30)
print("🚀 STARTING IRONMAN HUD MODE 🚀")
print("==============================")

# --- CONFIGURATION ---
# Colors in BGR (Blue, Green, Red)
COLOR_CYAN = (255, 255, 0)     # The "Ironman" Blue
COLOR_RED = (0, 0, 255)        # Selection Color
BLOCK_SIZE = 40                # Size of the square blocks

# 1. Initialize MediaPipe
mp_hands = mp.solutions.hands
# Note: "min_detection_confidence" makes it stick to your hand better
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.85)
mp_draw = mp.solutions.drawing_utils

# 2. Setup Camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# 3. Create the Drawing Canvas
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

xp, yp = 0, 0 # Previous coordinates

while True:
    # A. Get Frame
    success, img = cap.read()
    if not success:
        print("Camera not found!")
        break
        
    img = cv2.flip(img, 1) # Mirror

    # B. Find Hand
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            
            # --- VISUAL UPGRADE: Draw Robotic Connections ---
            # Instead of default red dots, we draw Cyan lines manually
            mp_draw.draw_landmarks(
                img, 
                hand_lms, 
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=2, circle_radius=4), # Joints
                mp_draw.DrawingSpec(color=COLOR_CYAN, thickness=2)  # Lines
            )

            # Get Finger Tip Coordinates
            lmList = []
            for id, lm in enumerate(hand_lms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
            
            if len(lmList) != 0:
                # Index Tip (8) & Middle Tip (12)
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]

                # Check Fingers Up
                fingers = []
                # Index
                if lmList[8][2] < lmList[6][2]: fingers.append(1)
                else: fingers.append(0)
                # Middle
                if lmList[12][2] < lmList[10][2]: fingers.append(1)
                else: fingers.append(0)

                # --- SELECTION MODE (Two Fingers) ---
                if fingers[0] == 1 and fingers[1] == 1:
                    xp, yp = 0, 0 
                    cv2.rectangle(img, (x1-20, y1-20), (x2+20, y2+20), COLOR_RED, 2)
                    cv2.putText(img, "TARGET LOCKED", (x1, y1-30), cv2.FONT_HERSHEY_PLAIN, 1, COLOR_RED, 2)

                # --- DRAWING MODE (Index Finger Only) ---
                elif fingers[0] == 1 and fingers[1] == 0:
                    
                    # Draw the "Cursor" Block
                    cv2.rectangle(img, (x1-25, y1-25), (x1+25, y1+25), COLOR_CYAN, 2)
                    
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1
                    
                    # DRAW BLOCKS (Interpolation for smooth lines)
                    steps = 10
                    for i in range(steps):
                        # Calculate points between previous and current location
                        inter_x = int(xp + (x1 - xp) * i / steps)
                        inter_y = int(yp + (y1 - yp) * i / steps)
                        
                        # Draw filled SQUARE block on canvas
                        top_left = (inter_x - BLOCK_SIZE//2, inter_y - BLOCK_SIZE//2)
                        bottom_right = (inter_x + BLOCK_SIZE//2, inter_y + BLOCK_SIZE//2)
                        
                        cv2.rectangle(imgCanvas, top_left, bottom_right, COLOR_CYAN, cv2.FILLED)
                    
                    xp, yp = x1, y1

    # C. Combine Canvas + Video
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 10, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    
    # "Black out" the area where we drew, then add the color back
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    cv2.imshow("Ironman HUD", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break