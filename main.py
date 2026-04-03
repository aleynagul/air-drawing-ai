import cv2
import time

from src.hand_tracking import HandTracker
from src.drawing import AirDrawer

#Kamera başlat
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

tracker = HandTracker()
drawer = AirDrawer()

prev_time = 0
prev_point = None
lost_counter = 0


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # FPS kontrol (her frame hesaplama yapma)
    current_time = time.time()
    if current_time - prev_time > 0.02:
        point = tracker.get_hand_position(frame)
        prev_time = current_time
    else:
        point = None

    #smoothing (titreşim azaltma)
    if point and prev_point:
        point = (
            int((point[0] + prev_point[0]) / 2),
            int((point[1] + prev_point[1]) / 2)
        )

    prev_point = point

    # çizim
    if point:
        frame = drawer.draw(frame, point)
        lost_counter = 0
    else:
        lost_counter += 1
        if lost_counter > 5: 
            #son noktayı koru kopma olmasın
            drawer.last_point = None 
        prev_valid=False    

    # ekrana bas
    cv2.imshow("Air Drawing AI ", frame)

    # tuş kontrolü
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('c'):
        drawer.reset()

#çıkış
cap.release()
cv2.destroyAllWindows()