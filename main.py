import cv2
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk

from src.hand_tracking import HandTracker
from src.drawing import AirDrawer

# Kamera başlat
cap = cv2.VideoCapture(0)


tracker = HandTracker()
drawer = AirDrawer()

prev_point = None
thickness = 5
color = (255, 0, 255)  # default pembe 

# tkinter
root = tk.Tk()
root.title("Air Drawing Control Panel")

# renk seçimi için yardımcı fonksiyonlar
def hex_to_rgb(hex):
    return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))

def choose_color():
    global color
    color_code = colorchooser.askcolor(title="Choose color")[1]
    if color_code:
        color = hex_to_rgb(color_code)

#screen üzerindeki renk kutularına tıklama ile renk seçimi
def check_color_selection(x, y):
    global color

    if 20 < x < 100 and 20 < y < 100:
        color = (0, 0, 255)       # kırmızı
    elif 120 < x < 200 and 20 < y < 100:
        color = (0, 255, 0)       # yeşil
    elif 220 < x < 300 and 20 < y < 100:
        color = (255, 0, 0)       # mavi
    elif 320 < x < 400 and 20 < y < 100:
        color = (0, 255, 255)     # sarı
    elif 420 < x < 500 and 20 < y < 100:
        color = (255, 0, 255)     # pembe 

#thickness artırma ve azaltma fonksiyonları
def increase_thickness():
    global thickness
    thickness += 1

def decrease_thickness():
    global thickness
    thickness = max(1, thickness - 1)

# kontroller için butonlar
tk.Button(root, text="Choose Color", command=choose_color).pack()
tk.Button(root, text="Increase Thickness", command=increase_thickness).pack()
tk.Button(root, text="Decrease Thickness", command=decrease_thickness).pack()

ret, frame = cap.read()
h, w, _ = frame.shape

canvas = tk.Canvas(root, width=w, height=h)
canvas.pack()

def update_frame():
    global color, thickness

    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return

    frame = cv2.flip(frame, 1)
    

    # renk kutuları çizimi
    cv2.rectangle(frame, (20, 20), (100, 100), (0, 0, 255), -1)
    cv2.rectangle(frame, (120, 20), (200, 100), (0, 255, 0), -1)
    cv2.rectangle(frame, (220, 20), (300, 100), (255, 0, 0), -1)
    cv2.rectangle(frame, (320, 20), (400, 100), (0, 255, 255), -1)
    cv2.rectangle(frame, (420, 20), (500, 100), (255, 0, 255), -1)

    landmarks = tracker.get_landmarks(frame)

    if landmarks:
        fingers = tracker.count_fingers(landmarks)

        h, w, _ = frame.shape
        x = int(landmarks[8].x * w)
        y = int(landmarks[8].y * h)
        point = (x, y)
        
        check_color_selection(x, y)

        global prev_point
        if prev_point is not None:
             point = (
        int((point[0] + prev_point[0]) / 2),
        int((point[1] + prev_point[1]) / 2)
            )

        prev_point = point
        
        if fingers == 1:
            frame = drawer.draw(frame, point, color, thickness)
        elif fingers == 2:
            # drawer.last_point = None  
            frame = drawer.erase(frame, point, 40) 

    else:
        drawer.last_point = None
        prev_point = None

    # seçilen renk ve kalınlık bilgisini ekrana yazma
    cv2.rectangle(frame, (20, 120), (100, 200), color, -1)
    cv2.putText(frame, f"Thick: {thickness}", (120, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)

    canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    canvas.image = imgtk

    root.after(10, update_frame)

#klavye kısayolları
def handle_keys(event):
    global color, thickness

    if event.char == 'q':
        cap.release()
        cv2.destroyAllWindows()
        root.quit()

    elif event.char == 'c':
        drawer.reset()

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