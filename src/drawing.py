import cv2

class AirDrawer:
    def __init__(self):
        self.canvas = None
        self.last_point = None
        self.thickness = 5
        self.color = (255, 0, 255)  # default renk (pembe)

    def initialize_canvas(self, frame):
        if self.canvas is None:
            self.canvas = frame.copy() * 0  # siyah boş canvas

    #önceki nokta ile yeni nokta arasında çizgi çizme
    def draw(self, frame, point,color, thickness):
        self.initialize_canvas(frame)

        if self.last_point is not None:
            cv2.line(self.canvas, self.last_point, point, color, thickness)
        #yeni noktayı kaydet
        self.last_point = point

        # canvas + kamera birleşimi
        return cv2.add(frame, self.canvas)

    def reset(self):
        self.canvas = None
        self.last_point = None