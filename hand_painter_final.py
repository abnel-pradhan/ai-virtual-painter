import cv2
import mediapipe as mp
import numpy as np

# 1. Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.85)
mp_draw = mp.solutions.drawing_utils

# 2. Setup Camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280) # Width
cap.set(4, 720)  # Height

# 3. Create a Canvas to draw on
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

# Variables for drawing
xp, yp = 0, 0 # Previous coordinates
drawColor = (255, 0, 255) # Purple
brushThickness = 15

while True:
    # A. Import Image
    success, img = cap.read()
    img = cv2.flip(img, 1) # Flip for mirror effect

    # B. Find Hand Landmarks
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # Get Landmark positions
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if len(lmList) != 0:
                # Tip of Index finger (8) and Middle finger (12)
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]

                # C. Check which fingers are up
                # Only Index Up = Drawing Mode
                # Both Index and Middle Up = Selection/Hover Mode
                fingers = []
                # Index finger
                if lmList[8][2] < lmList[6][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                # Middle finger
                if lmList[12][2] < lmList[10][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

                # D. SELECTION MODE (Two fingers up)
                if fingers[0] == 1 and fingers[1] == 1:
                    xp, yp = 0, 0 # Reset drawing path
                    cv2.circle(img, (x1, y1), 15, (255, 255, 255), cv2.FILLED)
                    print("Selection Mode")

                # E. DRAWING MODE (Only Index finger up)
                elif fingers[0] == 1 and fingers[1] == 0:
                    cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                    print("Drawing Mode")
                    
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    # Draw on the canvas
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
                    xp, yp = x1, y1

    # F. Merge Canvas and Video
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    cv2.imshow("Virtual Painter", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break