import cv2
import time

from src.hand_tracking import HandTracker
from src.drawing import AirDrawer

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

tracker = HandTracker()
drawer = AirDrawer()

prev_time = 0
prev_point = None
thickness = 5
color=(255, 0, 255)
alpha = 0.3  # Smoothing için ayar (daha düşük daha hızlı, daha yüksek daha yumuşak)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    point = None
    landmarks = None

    current_time = time.time()
    if current_time - prev_time > 0.02:
        landmarks = tracker.get_landmarks(frame)
        prev_time = current_time

    if landmarks:
        fingers = tracker.count_fingers(landmarks)

        h, w, _ = frame.shape
        x = int(landmarks[8].x * w)
        y = int(landmarks[8].y * h)
        point = (x, y)

        # Smooth çizim
        if prev_point is not None:
            point = (
                int(alpha * point[0] + (1 - alpha) * prev_point[0]),
                int(alpha * point[1] + (1 - alpha) * prev_point[1])
            )

        prev_point = point

        # Gesture kontrolü
        if fingers == 1:
            frame = drawer.draw(frame, point, color, drawer.thickness)
        elif fingers == 2:
            drawer.last_point = None  # çizimi durdur

    else:
        # El kaybolduğunda çizim kaybolmasın
        drawer.last_point = None
        prev_point = None

    cv2.imshow("Air Drawing AI ", frame)

    key = cv2.waitKey(1)
  
    if key == ord('q'):
        break
    elif key == ord('c'):
        drawer.reset()
      #renkler
    elif key == ord('r'):
         color = (0, 0, 255)  # kırmızı
    elif key == ord('g'):
     color = (0, 255, 0)  # yeşil
    elif key == ord('b'):
        color = (255, 0, 0)  # mavi   
    #kalıklık arttırma 
    elif key == ord('t'):
        drawer.thickness += 1
    elif key == ord('y'):
        drawer.thickness = max(1, drawer.thickness - 1)  # kalınlığı azaltırken minimum 1 yap   
        

cap.release()
cv2.destroyAllWindows()