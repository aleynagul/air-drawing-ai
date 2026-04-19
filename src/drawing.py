import cv2
import numpy as np
from collections import deque

from src.config import MAX_UNDO_HISTORY, SPRAY_SIZE, SPRAY_DENSITY


class AirDrawer:
    def __init__(self):
        self.canvas     = None
        self.last_point = None
        self.history    = deque(maxlen=MAX_UNDO_HISTORY)
        self.redo_stack = []


    def _init_canvas(self, frame):
        if self.canvas is None:
            self.canvas = np.zeros_like(frame)

    def _save_state(self):
        if self.canvas is not None:
            self.history.append(self.canvas.copy())
            self.redo_stack.clear()

    def _render(self, frame):
        glow   = cv2.GaussianBlur(self.canvas, (25, 25), 0)
        output = cv2.addWeighted(frame, 1,      self.canvas, 1,   0)
        output = cv2.addWeighted(output, 1,     glow,        0.5, 0)
        return output


    def draw(self, frame, point, color, thickness):
        self._init_canvas(frame)
        if self.last_point is not None:
            self._save_state()
            cv2.line(self.canvas, self.last_point, point, color, thickness)
        self.last_point = point
        return self._render(frame)

    def erase(self, frame, point, size=None):
        from src.config import ERASER_SIZE
        size = size or ERASER_SIZE
        self._init_canvas(frame)
        self._save_state()
        cv2.circle(self.canvas, point, size, (0, 0, 0), -1)
        return self._render(frame)

    def spray(self, frame, point, color, size=None, density=None):
        size    = size    or SPRAY_SIZE
        density = density or SPRAY_DENSITY
        self._init_canvas(frame)
        self._save_state()
        for _ in range(density):
            angle  = np.random.uniform(0, 2 * np.pi)
            radius = np.random.uniform(0, size)
            px = int(point[0] + radius * np.cos(angle))
            py = int(point[1] + radius * np.sin(angle))
            cv2.circle(self.canvas, (px, py), 1, color, -1)
        return self._render(frame)

    def undo(self):
        if self.history:
            self.redo_stack.append(self.canvas.copy())
            self.canvas     = self.history.pop()
            self.last_point = None

    def redo(self):
        if self.redo_stack:
            self.history.append(self.canvas.copy())
            self.canvas     = self.redo_stack.pop()
            self.last_point = None

    def reset(self):
        self._save_state()
        if self.canvas is not None:
            self.canvas = np.zeros_like(self.canvas)
        self.last_point = None