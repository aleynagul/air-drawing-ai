import cv2
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk

from src.hand_tracking  import HandTracker
from src.drawing        import AirDrawer
from src.canvas_manager import draw_ui, check_color_selection, is_in_palette
from src.config import (
    CAMERA_INDEX, DEFAULT_COLOR, DEFAULT_THICKNESS,
    ERASER_SIZE, SMOOTHING_ALPHA, LOST_FRAME_LIMIT,
)


def hex_to_bgr(hex_code):
    r, g, b = (int(hex_code[i:i+2], 16) for i in (1, 3, 5))
    return (b, g, r)  


def draw_with_interpolation(frame, drawer, prev_pt, curr_pt, color, thickness):
    if prev_pt is None:
        return drawer.draw(frame, curr_pt, color, thickness)

    x1, y1 = prev_pt
    x2, y2 = curr_pt
    dist  = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    steps = max(1, int(dist / 5))

    for i in range(steps + 1):
        t  = i / steps
        ix = int(x1 + t * (x2 - x1))
        iy = int(y1 + t * (y2 - y1))
        frame = drawer.draw(frame, (ix, iy), color, thickness)

    return frame


class AirDrawingApp:
    def __init__(self):
        self.cap       = cv2.VideoCapture(CAMERA_INDEX)
        self.tracker   = HandTracker()
        self.drawer    = AirDrawer()

        self.color     = DEFAULT_COLOR
        self.thickness = DEFAULT_THICKNESS
        self.prev_point  = None
        self.lost_counter = 0

        self._build_ui()


    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Air Drawing Control Panel")

        tk.Button(self.root, text="Choose Color",       command=self._choose_color).pack()
        tk.Button(self.root, text="Increase Thickness", command=self._increase_thickness).pack()
        tk.Button(self.root, text="Decrease Thickness", command=self._decrease_thickness).pack()

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Kamera başlatılamadı.")
        h, w, _ = frame.shape
        self.frame_w = w
        self.frame_h = h

        self.canvas_widget = tk.Canvas(self.root, width=w, height=h)
        self.canvas_widget.pack()

        self.root.bind("<Key>", self._handle_keys)

    def _choose_color(self):
        code = colorchooser.askcolor(title="Choose color")[1]
        if code:
            self.color = hex_to_bgr(code)

    def _increase_thickness(self):
        self.thickness += 1

    def _decrease_thickness(self):
        self.thickness = max(1, self.thickness - 1)

    def _handle_keys(self, event):
        key = event.char
        if key == 'q':
            self.cap.release()
            cv2.destroyAllWindows()
            self.root.quit()
        elif key == 'c':
            self.drawer.reset()
        elif key == 'z':
            self.drawer.undo()
        elif key == 'y':
            self.drawer.redo()
        elif key == 'r':
            self.color = (0, 0, 255)
        elif key == 'g':
            self.color = (0, 255, 0)
        elif key == 'b':
            self.color = (255, 0, 0)
        elif key == '+':
            self.thickness += 1
        elif key == '-':
            self.thickness = max(1, self.thickness - 1)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame)
            return

        frame     = cv2.flip(frame, 1)
        w, h      = self.frame_w, self.frame_h
        landmarks = self.tracker.get_landmarks(frame.copy())
        mode_text = "NONE"

        if landmarks:
            self.lost_counter = 0
            fingers = self.tracker.count_fingers(landmarks)

            x = int(landmarks[8].x * w)
            y = int(landmarks[8].y * h)

            if self.prev_point is not None:
                point = (
                    int(SMOOTHING_ALPHA * x + (1 - SMOOTHING_ALPHA) * self.prev_point[0]),
                    int(SMOOTHING_ALPHA * y + (1 - SMOOTHING_ALPHA) * self.prev_point[1]),
                )
            else:
                point = (x, y)

            self.prev_point = point

            selected = check_color_selection(x, y)
            if selected:
                self.color = selected

            if is_in_palette(x, y):
                mode_text = "COLOR SELECT"
            else:
                if fingers == 1:
                    mode_text = "DRAW"
                    frame = draw_with_interpolation(
                        frame, self.drawer,
                        self.prev_point, point,
                        self.color, self.thickness,
                    )
                elif fingers == 2:
                    mode_text = "ERASE"
                    frame = self.drawer.erase(frame, point, ERASER_SIZE)

                elif fingers == 3:
                    mode_text = "SPRAY"
                    frame = self.drawer.spray(frame, point, self.color)
                    self.drawer.last_point = None

                elif fingers == 4:
                    mode_text = "RESET"
                    self.drawer.reset()
                    self.drawer.last_point = None
                    self.prev_point = None

                elif fingers == 5:
                    mode_text = "UNDO"
                    self.drawer.undo()
                    self.prev_point = None

                else:
                    mode_text = "PAUSE"
                    self.drawer.last_point = None

        else:
            self.lost_counter += 1
            if self.lost_counter > LOST_FRAME_LIMIT:
                self.drawer.last_point = None
                self.prev_point = None

        frame = draw_ui(frame, self.color, self.thickness, mode_text)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img    = Image.fromarray(frame_rgb)
        imgtk  = ImageTk.PhotoImage(image=img)
        self.canvas_widget.create_image(0, 0, anchor=tk.NW, image=imgtk)
        self.canvas_widget.image = imgtk

        self.root.after(10, self.update_frame)

    def run(self):
        self.update_frame()
        self.root.mainloop()