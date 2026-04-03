import cv2

class AirDrawer:
    def __init__(self):
        self.canvas = None
        self.last_point = None

    def initialize_canvas(self, frame):
        if self.canvas is None:
            self.canvas = frame.copy() * 0  # siyah boş canvas

    #önceki nokta ile yeni nokta arasında çizgi çizme
    def draw(self, frame, point):
        self.initialize_canvas(frame)

        if self.last_point is not None:
            cv2.line(self.canvas, self.last_point, point, (255, 0, 255), 5)

        #yeni noktayı kaydet
        self.last_point = point

        # canvas + kamera birleşimi
        return cv2.add(frame, self.canvas)

    def reset(self):
        self.canvas = None
        self.last_point = None