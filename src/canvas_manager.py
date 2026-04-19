import cv2

from src.config import (
    PANEL_X, PANEL_Y, PANEL_W, PANEL_H,
    PALETTE_COLORS,
)


MODE_COLORS = {
    "DRAW":         (120, 220, 120),
    "ERASE":        (100, 180, 255),
    "RESET":        (80,  80,  220),
    "PAUSE":        (160, 160, 160),
    "COLOR SELECT": (255, 200, 80),
    "UNDO":         (255, 140, 80),
    "NONE":         (100, 100, 100),
    "SPRAY":        (200, 100, 255),
}


def draw_ui(frame, color, thickness, mode_text):

    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (PANEL_X, PANEL_Y),
        (PANEL_X + PANEL_W, PANEL_Y + PANEL_H),
        (30, 30, 30), -1,
    )
    frame = cv2.addWeighted(overlay, 0.45, frame, 0.55, 0)
    
    cv2.rectangle(
        frame,
        (PANEL_X, PANEL_Y),
        (PANEL_X + PANEL_W, PANEL_Y + PANEL_H),
        (255, 255, 255), 1,
    )

    for i, c in enumerate(PALETTE_COLORS):
        cx = PANEL_X + PANEL_W // 2
        cy = PANEL_Y + 35 + i * 52

        if c == color:
            cv2.circle(frame, (cx, cy), 22, (255, 255, 255), 2)

        cv2.circle(frame, (cx, cy), 18, c, -1)
        cv2.circle(frame, (cx, cy), 18, (200, 200, 200), 1)

    bar_y = PANEL_Y + 340
    cv2.putText(
        frame, "SIZE",
        (PANEL_X + 18, bar_y),
        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1,
    )
    for i in range(1, 6):
        bar_x  = PANEL_X + 10 + i * 14
        filled = i <= min(thickness // 2 + 1, 5)
        col    = (255, 255, 255) if filled else (80, 80, 80)
        cv2.circle(frame, (bar_x, bar_y + 18), i + 1, col, -1)

    mode_col = MODE_COLORS.get(mode_text, (200, 200, 200))
    cv2.rectangle(
        frame,
        (PANEL_X + 6,          PANEL_Y + PANEL_H - 42),
        (PANEL_X + PANEL_W - 6, PANEL_Y + PANEL_H - 8),
        mode_col, -1,
    )
    cv2.putText(
        frame, mode_text,
        (PANEL_X + 10, PANEL_Y + PANEL_H - 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.32, (20, 20, 20), 1,
    )

    return frame


def check_color_selection(x, y):
    for i, c in enumerate(PALETTE_COLORS):
        cx = PANEL_X + PANEL_W // 2
        cy = PANEL_Y + 35 + i * 52
        if abs(x - cx) < 22 and abs(y - cy) < 22:
            return c
    return None


def is_in_palette(x, y):
    return check_color_selection(x, y) is not None