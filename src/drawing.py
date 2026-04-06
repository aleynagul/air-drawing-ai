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
            #normal çizgi çizme
            cv2.line(self.canvas, self.last_point, point, color, thickness)
        #yeni noktayı kaydet
        self.last_point = point
        #blur efekti
        glow = cv2.GaussianBlur(self.canvas, (25, 25), 0)
        
        output = frame.copy()
        #birleştirme işlemi
        output = cv2.addWeighted(output, 1, self.canvas, 1, 0)
        output = cv2.addWeighted(output, 1, glow, 0.5, 0)
            
        # canvas + kamera birleşimi
        return output

    def erase(self,frame,point,size=30):
        self.initialize_canvas(frame)
        #silme işlemi için büyük bir siyah daire 
        cv2.circle(self.canvas, point, size, (0,0,0), -1)
        return cv2.add(frame, self.canvas)

    def reset(self):
        self.canvas = None
        self.last_point = None
        