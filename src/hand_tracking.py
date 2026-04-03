import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks import python

class HandTracker:
    def __init__(self):
        #makine öğrenmesi modelini yükleme(el tanımayı yapan ai modeli)
        base_options = python.BaseOptions(
             model_asset_path="models/hand_landmarker.task"
        )
        
        #maksimum 1 el tanımak için            
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def get_hand_position(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        #el var mı,nerede?
        result = self.detector.detect(mp_image)

        if result.hand_landmarks:
            #ilk elin noktaları(21 nokta)
            landmarks = result.hand_landmarks[0]

            h, w, _ = frame.shape
            #landmark 8, işaret parmağının ucu
            #normalize edilmiş koordinatları piksel koordinatlarına çevirme
            x = int(landmarks[8].x * w)
            y = int(landmarks[8].y * h)

            return (x, y)

        return None