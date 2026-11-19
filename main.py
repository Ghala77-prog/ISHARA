
import cv2
import mediapipe as mp
import pyautogui
import math
import time
import sys

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================
# ISHARA - GESTURE CONTROL SYSTEM
# WINDOWS DESKTOP APPLICATION
# ============================================


# ============================================
# CONFIGURATION
# ============================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "hand_landmarker.task"

SMOOTHING = 0.2
MARGIN = 0.1

PINCH_THRESHOLD = 0.045
RELEASE_THRESHOLD = 0.07

SCROLL_THRESHOLD = 0.018
SCROLL_STEP = 2
SCROLL_COOLDOWN = 0.12

GESTURE_HOLD = 0.65
FIST_HOLD = 1.0
PALM_HOLD = 2.0

pyautogui.FAILSAFE = True

SCREEN_W, SCREEN_H = pyautogui.size()


# ============================================
# DESIGN COLORS - BGR FORMAT
# ============================================

BG = (17, 23, 19)
PANEL = (24, 32, 26)
PANEL_LIGHT = (35, 45, 37)

GREEN = (125, 245, 145)
GREEN_DARK = (45, 90, 55)

WHITE = (240, 245, 240)
MUTED = (160, 175, 160)

BORDER = (65, 95, 65)

RED = (80, 85, 190)
RED_DARK = (40, 43, 85)

YELLOW = (100, 210, 245)


# ============================================
# APPLICATION STATE
# ============================================

mode = "MOUSE"
mouse_enabled = False
running = True

smooth_x = SCREEN_W / 2
smooth_y = SCREEN_H / 2

left_frames = 0
right_frames = 0

left_pressed = False
right_pressed = False

previous_scroll_y = None
last_scroll_time = 0

gesture_candidate = None
gesture_start = 0
gesture_fired = False

fist_start = None
palm_start = None
palm_used = False

status = "READY"

WINDOW_NAME = "ISHARA"

buttons = {}


# ============================================
# HELPER FUNCTIONS
# ============================================

def distance(a, b):
    return math.hypot(
        a.x - b.x,
        a.y - b.y
    )


def finger_up(lm, tip, pip):
    return lm[tip].y < lm[pip].y


def reset_mouse():

    global left_frames
    global right_frames
    global left_pressed
    global right_pressed
    global previous_scroll_y

    left_frames = 0
    right_frames = 0

    left_pressed = False
    right_pressed = False

    previous_scroll_y = None


def reset_presentation():

    global gesture_candidate
    global gesture_start
    global gesture_fired

    gesture_candidate = None
    gesture_start = 0
    gesture_fired = False


def change_mode(new_mode):

    global mode
    global mouse_enabled
    global fist_start
    global palm_start
    global palm_used
    global status

    mode = new_mode

    # Keep mouse paused after switching modes
    mouse_enabled = False

    reset_mouse()
    reset_presentation()

    fist_start = None
    palm_start = None
    palm_used = True

    status = f"{mode} MODE"


# ============================================
# DRAW HAND TRACKING
# ============================================

def draw_hand(frame, lm):

    h, w = frame.shape[:2]

    connections = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        (0, 17)
    ]

    # Draw neon green connections
    for a, b in connections:

        p1 = (
            int(lm[a].x * w),
            int(lm[a].y * h)
        )

        p2 = (
            int(lm[b].x * w),
            int(lm[b].y * h)
        )

        cv2.line(
            frame,
            p1,
            p2,
            GREEN,
            2,
            cv2.LINE_AA
        )

    # Draw tracking points
    for point in lm:

        x = int(point.x * w)
        y = int(point.y * h)

        cv2.circle(
            frame,
            (x, y),
            5,
            GREEN_DARK,
            -1,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            (x, y),
            2,
            WHITE,
            -1,
            cv2.LINE_AA
        )


# ============================================
# DRAW TEXT
# ============================================

def draw_text(
    frame,
    text,
    x,
    y,
    scale=0.45,
    color=WHITE,
    thickness=1
):

    cv2.putText(
        frame,
        text,
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def text_width(text, scale=0.45, thickness=1):

    size = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        thickness
    )[0]

    return size[0]


# ============================================
# MOUSE BUTTON CALLBACK
# ============================================

def mouse_callback(event, x, y, flags, param):

    global running
    global mouse_enabled
    global status

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    for name, rect in buttons.items():

        x1, y1, x2, y2 = rect

        if x1 <= x <= x2 and y1 <= y <= y2:

            if name == "MOUSE":

                change_mode("MOUSE")

            elif name == "PRESENTATION":

                change_mode("PRESENTATION")

            elif name == "PAUSE":

                if mode == "MOUSE":

                    mouse_enabled = not mouse_enabled

                    reset_mouse()

                    status = (
                        "MOUSE ACTIVE"
                        if mouse_enabled
                        else "MOUSE PAUSED"
                    )

            elif name == "EXIT":

                running = False

            break


# ============================================
# DRAW BUTTON
# ============================================

def draw_button(
    frame,
    name,
    label,
    x1,
    y1,
    x2,
    y2,
    selected=False,
    disabled=False
):

    if disabled:

        fill = (28, 32, 29)
        edge = (48, 55, 49)
        text_color = (95, 110, 98)

    elif name == "EXIT":

        fill = RED_DARK
        edge = RED
        text_color = WHITE

    elif selected:

        fill = GREEN_DARK
        edge = GREEN
        text_color = WHITE

    else:

        fill = PANEL_LIGHT
        edge = BORDER
        text_color = WHITE

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        fill,
        -1
    )

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        edge,
        1
    )

    scale = (
        0.32
        if label == "PRESENTATION"
        else 0.43
    )

    tw = text_width(label, scale)

    tx = x1 + max(
        3,
        ((x2 - x1) - tw) // 2
    )

    ty = y1 + ((y2 - y1) + 10) // 2

    draw_text(
        frame,
        label,
        tx,
        ty,
        scale,
        text_color
    )


# ============================================
# DRAW INTERFACE
# ============================================

def draw_interface(
    frame,
    hand_detected=False,
    progress=0.0
):

    global buttons

    h, w = frame.shape[:2]

    overlay = frame.copy()

    header_h = 110
    footer_h = 112

    # Header background
    cv2.rectangle(
        overlay,
        (0, 0),
        (w, header_h),
        PANEL,
        -1
    )

    # Footer background
    cv2.rectangle(
        overlay,
        (0, h - footer_h),
        (w, h),
        PANEL,
        -1
    )

    cv2.addWeighted(
        overlay,
        0.95,
        frame,
        0.05,
        0,
        frame
    )

    # Separators
    cv2.line(
        frame,
        (0, header_h),
        (w, header_h),
        BORDER,
        1
    )

    cv2.line(
        frame,
        (0, h - footer_h),
        (w, h - footer_h),
        BORDER,
        1
    )

    # ====================================
    # APP TITLE
    # ====================================

    draw_text(
        frame,
        "ISHARA",
        22,
        38,
        0.95,
        GREEN,
        2
    )

    draw_text(
        frame,
        "GESTURE CONTROL SYSTEM",
        24,
        60,
        0.39,
        MUTED
    )

    # ====================================
    # CURRENT MODE
    # ====================================

    mode_label = (
        "PRESENTATION"
        if mode == "PRESENTATION"
        else "MOUSE"
    )

    mw = text_width(mode_label, 0.48)

    draw_text(
        frame,
        mode_label,
        max(18, w - mw - 22),
        36,
        0.48,
        GREEN
    )

    # ====================================
    # HAND STATUS
    # ====================================

    hand_label = (
        "HAND DETECTED"
        if hand_detected
        else "NO HAND DETECTED"
    )

    hand_color = (
        GREEN
        if hand_detected
        else YELLOW
    )

    cv2.circle(
        frame,
        (27, 88),
        6,
        hand_color,
        -1,
        cv2.LINE_AA
    )

    draw_text(
        frame,
        hand_label,
        43,
        93,
        0.43,
        hand_color
    )

    # ====================================
    # CURRENT ACTION
    # ====================================

    action_label = status[:25]

    aw = text_width(action_label, 0.42)

    draw_text(
        frame,
        action_label,
        max(20, w - aw - 22),
        92,
        0.42,
        WHITE
    )

    # ====================================
    # CAMERA CORNER FRAME
    # ====================================

    x1 = 22
    x2 = w - 22

    y1 = header_h + 15
    y2 = h - footer_h - 15

    corner = 23

    if x2 > x1 + 30 and y2 > y1 + 30:

        for x, sx in (
            (x1, 1),
            (x2, -1)
        ):

            for y, sy in (
                (y1, 1),
                (y2, -1)
            ):

                cv2.line(
                    frame,
                    (x, y),
                    (x + sx * corner, y),
                    GREEN,
                    2
                )

                cv2.line(
                    frame,
                    (x, y),
                    (x, y + sy * corner),
                    GREEN,
                    2
                )

    # ====================================
    # GESTURE PROGRESS
    # ====================================

    progress = max(
        0.0,
        min(1.0, progress)
    )

    if progress > 0:

        bar_x1 = 24
        bar_x2 = w - 24

        bar_y1 = h - footer_h - 8
        bar_y2 = h - footer_h - 3

        cv2.rectangle(
            frame,
            (bar_x1, bar_y1),
            (bar_x2, bar_y2),
            PANEL_LIGHT,
            -1
        )

        filled = int(
            (bar_x2 - bar_x1) * progress
        )

        cv2.rectangle(
            frame,
            (bar_x1, bar_y1),
            (bar_x1 + filled, bar_y2),
            GREEN,
            -1
        )

    # ====================================
    # INSTRUCTIONS
    # ====================================

    if mode == "PRESENTATION":

        instructions = (
            "1 finger: Next  |  "
            "2 fingers: Previous  |  "
            "Fist: Exit"
        )

    else:

        instructions = (
            "Pinch: Click  |  "
            "2 fingers: Scroll  |  "
            "Palm: Switch"
        )

    draw_text(
        frame,
        instructions,
        22,
        h - 83,
        0.40,
        MUTED
    )

    # ====================================
    # BUTTONS
    # ====================================

    names = [
        "MOUSE",
        "PRESENTATION",
        "PAUSE",
        "EXIT"
    ]

    buttons = {}

    margin = 14
    gap = 8

    button_w = max(
        1,
        (w - 2 * margin - 3 * gap) // 4
    )

    by1 = h - 65
    by2 = h - 15

    for i, name in enumerate(names):

        bx1 = margin + i * (button_w + gap)
        bx2 = bx1 + button_w

        buttons[name] = (
            bx1,
            by1,
            bx2,
            by2
        )

        selected = (
            (name == "MOUSE" and mode == "MOUSE")
            or (
                name == "PRESENTATION"
                and mode == "PRESENTATION"
            )
            or (
                name == "PAUSE"
                and mode == "MOUSE"
                and not mouse_enabled
            )
        )

        disabled = (
            name == "PAUSE"
            and mode == "PRESENTATION"
        )

        label = name

        if name == "PAUSE" and mode == "MOUSE":

            label = (
                "PAUSE"
                if mouse_enabled
                else "RESUME"
            )

        draw_button(
            frame,
            name,
            label,
            bx1,
            by1,
            bx2,
            by2,
            selected,
            disabled
        )


# ============================================
# MEDIAPIPE INITIALIZATION
# ============================================

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(
        model_asset_path=str(MODEL_PATH)
    ),
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(
    options
)


# ============================================
# CAMERA INITIALIZATION
# ============================================

# Keep this camera setup unchanged
cap = cv2.VideoCapture(0)

if not cap.isOpened():

    detector.close()

    raise RuntimeError(
        "Camera could not be opened"
    )


# ============================================
# WINDOW SETUP
# ============================================

cv2.namedWindow(
    WINDOW_NAME,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    WINDOW_NAME,
    800,
    600
)

cv2.setMouseCallback(
    WINDOW_NAME,
    mouse_callback
)


# ============================================
# MAIN APPLICATION LOOP
# ============================================

try:

    while running:

        success, frame = cap.read()

        if not success:

            print("Camera frame unavailable")
            break

        frame = cv2.flip(frame, 1)

        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = detector.detect(mp_image)

        status = "READY"
        progress = 0.0

        # ====================================
        # HAND DETECTED
        # ====================================

        if result.hand_landmarks:

            lm = result.hand_landmarks[0]

            draw_hand(frame, lm)

            index_up = finger_up(
                lm, 8, 6
            )

            middle_up = finger_up(
                lm, 12, 10
            )

            ring_up = finger_up(
                lm, 16, 14
            )

            pinky_up = finger_up(
                lm, 20, 18
            )

            now = time.time()

            fist = (
                not index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            )

            palm = (
                index_up
                and middle_up
                and ring_up
                and pinky_up
            )

            gesture_handled = False

            # =================================
            # OPEN PALM - SWITCH MODE
            # =================================

            if palm:

                if palm_start is None:
                    palm_start = now

                if not palm_used:

                    elapsed = now - palm_start

                    progress = min(
                        elapsed / PALM_HOLD,
                        1.0
                    )

                    if elapsed >= PALM_HOLD:

                        next_mode = (
                            "PRESENTATION"
                            if mode == "MOUSE"
                            else "MOUSE"
                        )

                        change_mode(next_mode)

                        gesture_handled = True

                    else:

                        status = "HOLD PALM TO SWITCH"

                        gesture_handled = True

                else:

                    status = "RELEASE PALM"
                    gesture_handled = True

            else:

                palm_start = None
                palm_used = False

            # =================================
            # FIST - EXIT PRESENTATION
            # =================================

            if mode == "PRESENTATION" and fist:

                if fist_start is None:
                    fist_start = now

                elapsed = now - fist_start

                progress = min(
                    elapsed / FIST_HOLD,
                    1.0
                )

                if elapsed >= FIST_HOLD:

                    change_mode("MOUSE")

                    status = "EXIT PRESENTATION"

                else:

                    status = "HOLD FIST TO EXIT"

                gesture_handled = True

            else:

                fist_start = None

            # =================================
            # MOUSE MODE
            # =================================

            if mode == "MOUSE" and not gesture_handled:

                reset_presentation()

                if mouse_enabled:

                    index = lm[8]

                    target_x = (
                        (index.x - MARGIN)
                        / (1 - 2 * MARGIN)
                    ) * SCREEN_W

                    target_y = (
                        (index.y - MARGIN)
                        / (1 - 2 * MARGIN)
                    ) * SCREEN_H

                    target_x = max(
                        0,
                        min(
                            SCREEN_W - 1,
                            target_x
                        )
                    )

                    target_y = max(
                        0,
                        min(
                            SCREEN_H - 1,
                            target_y
                        )
                    )

                    smooth_x += SMOOTHING * (
                        target_x - smooth_x
                    )

                    smooth_y += SMOOTHING * (
                        target_y - smooth_y
                    )

                    pyautogui.moveTo(
                        int(smooth_x),
                        int(smooth_y),
                        duration=0
                    )

                    left_dist = distance(
                        lm[4],
                        lm[8]
                    )

                    right_dist = distance(
                        lm[4],
                        lm[12]
                    )

                    scrolling = (
                        index_up
                        and middle_up
                        and not ring_up
                        and not pinky_up
                        and left_dist > RELEASE_THRESHOLD
                        and right_dist > RELEASE_THRESHOLD
                    )

                    if scrolling:

                        left_frames = 0
                        right_frames = 0

                        left_pressed = False
                        right_pressed = False

                        current_y = (
                            lm[8].y + lm[12].y
                        ) / 2

                        if previous_scroll_y is not None:

                            delta = (
                                previous_scroll_y
                                - current_y
                            )

                            if (
                                abs(delta) > SCROLL_THRESHOLD
                                and now - last_scroll_time
                                > SCROLL_COOLDOWN
                            ):

                                pyautogui.scroll(
                                    SCROLL_STEP
                                    if delta > 0
                                    else -SCROLL_STEP
                                )

                                last_scroll_time = now

                                previous_scroll_y = current_y

                                status = "SCROLL"

                        else:

                            previous_scroll_y = current_y

                    else:

                        previous_scroll_y = None

                        if left_dist < PINCH_THRESHOLD:

                            left_frames += 1

                        else:

                            left_frames = 0

                        if right_dist < PINCH_THRESHOLD:

                            right_frames += 1

                        else:

                            right_frames = 0

                        # LEFT CLICK
                        if (
                            left_frames >= 3
                            and not left_pressed
                            and right_dist > RELEASE_THRESHOLD
                        ):

                            pyautogui.click()

                            left_pressed = True

                            status = "LEFT CLICK"

                        # RIGHT CLICK
                        if (
                            right_frames >= 3
                            and not right_pressed
                            and left_dist > RELEASE_THRESHOLD
                        ):

                            pyautogui.click(
                                button="right"
                            )

                            right_pressed = True

                            status = "RIGHT CLICK"

                        if left_dist > RELEASE_THRESHOLD:

                            left_pressed = False

                        if right_dist > RELEASE_THRESHOLD:

                            right_pressed = False

                    if status == "READY":

                        status = "MOUSE ACTIVE"

                else:

                    status = "MOUSE PAUSED"

            # =================================
            # PRESENTATION MODE
            # =================================

            elif (
                mode == "PRESENTATION"
                and not gesture_handled
            ):

                # One finger = NEXT
                if (
                    index_up
                    and not middle_up
                    and not ring_up
                    and not pinky_up
                ):

                    gesture = "NEXT"

                # Two fingers = PREVIOUS
                elif (
                    index_up
                    and middle_up
                    and not ring_up
                    and not pinky_up
                ):

                    gesture = "PREVIOUS"

                else:

                    gesture = None

                if gesture is None:

                    reset_presentation()

                else:

                    if gesture != gesture_candidate:

                        gesture_candidate = gesture

                        gesture_start = now

                        gesture_fired = False

                    elapsed = now - gesture_start

                    if not gesture_fired:

                        progress = min(
                            elapsed / GESTURE_HOLD,
                            1.0
                        )

                    if (
                        elapsed >= GESTURE_HOLD
                        and not gesture_fired
                    ):

                        if gesture == "NEXT":

                            pyautogui.press("right")

                            status = "NEXT SLIDE"

                        else:

                            pyautogui.press("left")

                            status = "PREVIOUS SLIDE"

                        gesture_fired = True

                    elif gesture_fired:

                        status = f"{gesture} DONE"

                    else:

                        status = f"HOLD {gesture}"

        # ====================================
        # NO HAND DETECTED
        # ====================================

        else:

            reset_mouse()
            reset_presentation()

            fist_start = None
            palm_start = None
            palm_used = False

        # ====================================
        # RENDER INTERFACE
        # ====================================

        draw_interface(
            frame,
            hand_detected=bool(
                result.hand_landmarks
            ),
            progress=progress
        )

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        # ====================================
        # KEYBOARD SHORTCUTS
        # ====================================

        if key == ord("q") or key == 27:

            running = False

        elif key == ord("p"):

            change_mode(
                "PRESENTATION"
                if mode == "MOUSE"
                else "MOUSE"
            )

        elif key == ord("m") and mode == "MOUSE":

            mouse_enabled = not mouse_enabled

            reset_mouse()

        # ====================================
        # WINDOW CLOSE DETECTION
        # ====================================

        try:

            if cv2.getWindowProperty(
                WINDOW_NAME,
                cv2.WND_PROP_VISIBLE
            ) < 1:

                running = False

        except cv2.error:

            running = False


# ============================================
# CLEANUP
# ============================================

finally:

    cap.release()

    detector.close()

    cv2.destroyAllWindows()
