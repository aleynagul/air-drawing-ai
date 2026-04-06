import cv2
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk

from src.hand_tracking import HandTracker
from src.drawing import AirDrawer

# -----------------------------
# Başlatma
# -----------------------------
cap = cv2.VideoCapture(0)

tracker = HandTracker()
drawer = AirDrawer()

color = (255, 0, 255)
thickness = 5
prev_point = None
lost_counter = 0
alpha = 0.5
eraser_size = 40

# -----------------------------
# Tkinter pencere
# -----------------------------
root = tk.Tk()
root.title("Air Drawing Control Panel")

# -----------------------------
# Yardımcı fonksiyonlar
# -----------------------------
def draw_ui(frame, color, thickness, mode_text):
    overlay = frame.copy()

    panel_x, panel_y = 15, 15
    panel_w, panel_h = 90, 420

    cv2.rectangle(overlay,
                  (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  (30, 30, 30), -1)
    frame = cv2.addWeighted(overlay, 0.45, frame, 0.55, 0)

    cv2.rectangle(frame,
                  (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  (255, 255, 255), 1)

    colors = [
        (0, 0, 255),
        (0, 255, 0),
        (255, 0, 0),
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 255),
    ]

    for i, c in enumerate(colors):
        cx = panel_x + panel_w // 2
        cy = panel_y + 35 + i * 52

        if c == color:
            cv2.circle(frame, (cx, cy), 22, (255, 255, 255), 2)

        cv2.circle(frame, (cx, cy), 18, c, -1)
        cv2.circle(frame, (cx, cy), 18, (200, 200, 200), 1)

    bar_y = panel_y + 340
    cv2.putText(frame, "SIZE", (panel_x + 18, bar_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)

    for i in range(1, 6):
        bar_x = panel_x + 10 + i * 14
        filled = i <= min(thickness // 2 + 1, 5)
        col = (255, 255, 255) if filled else (80, 80, 80)
        cv2.circle(frame, (bar_x, bar_y + 18), i + 1, col, -1)

    mode_colors = {
        "DRAW":         (120, 220, 120),
        "ERASE":        (100, 180, 255),
        "RESET":        (80,  80,  220),
        "PAUSE":        (160, 160, 160),
        "COLOR SELECT": (255, 200, 80),
        "UNDO":         (255, 140, 80),
        "NONE":         (100, 100, 100),
        "SPRAY": (200, 100, 255),
    }
    mode_col = mode_colors.get(mode_text, (200, 200, 200))

    cv2.rectangle(frame,
                  (panel_x + 6, panel_y + panel_h - 42),
                  (panel_x + panel_w - 6, panel_y + panel_h - 8),
                  mode_col, -1)
    cv2.putText(frame, mode_text,
                (panel_x + 10, panel_y + panel_h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, (20, 20, 20), 1)

    return frame


def draw_with_interpolation(frame, drawer, prev_pt, curr_pt, color, thickness):
    if prev_pt is None:
        return drawer.draw(frame, curr_pt, color, thickness)

    x1, y1 = prev_pt
    x2, y2 = curr_pt
    dist = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    steps = max(1, int(dist / 5))

    for i in range(steps + 1):
        t = i / steps
        ix = int(x1 + t * (x2 - x1))
        iy = int(y1 + t * (y2 - y1))
        frame = drawer.draw(frame, (ix, iy), color, thickness)

    return frame


def hex_to_rgb(hex_code):
    return tuple(int(hex_code[i:i+2], 16) for i in (1, 3, 5))


def choose_color():
    global color
    color_code = colorchooser.askcolor(title="Choose color")[1]
    if color_code:
        color = hex_to_rgb(color_code)


def increase_thickness():
    global thickness
    thickness += 1


def decrease_thickness():
    global thickness
    thickness = max(1, thickness - 1)


def check_color_selection(x, y):
    global color
    colors = [
        (0, 0, 255), (0, 255, 0), (255, 0, 0),
        (0, 255, 255), (255, 0, 255), (255, 255, 255)
    ]
    for i, c in enumerate(colors):
        cx, cy = 60, 50 + i * 52
        if abs(x - cx) < 22 and abs(y - cy) < 22:
            color = c
            return


def is_in_palette(x, y):
    for i in range(6):
        cx, cy = 60, 50 + i * 52
        if abs(x - cx) < 22 and abs(y - cy) < 22:
            return True
    return False


# -----------------------------
# Butonlar
# -----------------------------
tk.Button(root, text="Choose Color", command=choose_color).pack()
tk.Button(root, text="Increase Thickness", command=increase_thickness).pack()
tk.Button(root, text="Decrease Thickness", command=decrease_thickness).pack()

# İlk frame ile canvas boyutu al
ret, frame = cap.read()
if not ret:
    raise RuntimeError("Kamera başlatılamadı.")

h, w, _ = frame.shape
canvas = tk.Canvas(root, width=w, height=h)
canvas.pack()

# -----------------------------
# Ana döngü
# -----------------------------
def update_frame():
    global color, thickness, prev_point, lost_counter

    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return

    frame = cv2.flip(frame, 1)

    # TAKİP İÇİN TEMİZ FRAME
    tracking_frame = frame.copy()
    landmarks = tracker.get_landmarks(tracking_frame)

    mode_text = "NONE"  # ← önce tanımla

    if landmarks:
        lost_counter = 0
        fingers = tracker.count_fingers(landmarks)

        x = int(landmarks[8].x * w)
        y = int(landmarks[8].y * h)
        point = (x, y)

        if prev_point is not None:
            point = (
                int(alpha * point[0] + (1 - alpha) * prev_point[0]),
                int(alpha * point[1] + (1 - alpha) * prev_point[1])
            )

        prev_point = point

        check_color_selection(x, y)
        in_palette = is_in_palette(x, y)

        if in_palette:
            mode_text = "COLOR SELECT"
        else:
            if fingers == 1:
                mode_text = "DRAW"
                frame = draw_with_interpolation(frame, drawer, prev_point, point, color, thickness)

            elif fingers == 2:
                mode_text = "ERASE"
                frame = drawer.erase(frame, point, eraser_size)
                
            elif fingers == 3:
                mode_text = "SPRAY"
                frame = drawer.spray(frame, point, color)
                drawer.last_point = None

            elif fingers == 4:
                mode_text = "RESET"
                drawer.reset()
                drawer.last_point = None
                prev_point = None

            elif fingers == 5:
                mode_text = "UNDO"
                drawer.undo()
                prev_point = None

            else:
                mode_text = "PAUSE"
                drawer.last_point = None 

    else:
        lost_counter += 1
        if lost_counter > 15:
            drawer.last_point = None
            prev_point = None

    # UI en son çizilir
    frame = draw_ui(frame, color, thickness, mode_text)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    canvas.image = imgtk

    root.after(10, update_frame)


# -----------------------------
# Klavye kısayolları
# -----------------------------
def handle_keys(event):
    global color, thickness

    if event.char == 'q':
        cap.release()
        cv2.destroyAllWindows()
        root.quit()

    elif event.char == 'c':
        drawer.reset()

    elif event.char == 'z':
        drawer.undo()

    elif event.char == 'y':
        drawer.redo()

    elif event.char == 'r':
        color = (0, 0, 255)

    elif event.char == 'g':
        color = (0, 255, 0)

    elif event.char == 'b':
        color = (255, 0, 0)

    elif event.char == '+':
        thickness += 1

    elif event.char == '-':
        thickness = max(1, thickness - 1)


root.bind("<Key>", handle_keys)

update_frame()
root.mainloop()