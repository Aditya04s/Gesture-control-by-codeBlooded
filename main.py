"""
main.py
---------------------------------
AI Gesture Experience v6.3
State Machine Architecture

Author: Shane
"""

import cv2
import time
import numpy as np

from modules.mode_controller import ModeController
from modules.detector import HandDetector
from modules.renderer import Renderer
from modules.motion import MotionEngine
from modules.gestures import GestureRecognizer
from modules.mouse import MouseController
from modules.ui import UI
from modules.worker import BackgroundWorker

from modules.screenshot import ScreenshotManager, ScreenshotState
from modules.scroll import ScrollManager
from modules.gesture_counter import GestureCounter

from modules.pose import PoseDetector

from modules.menu import ModeMenu
from modes.entertainment import EntertainmentMode
from modules.smart_context import SmartContextManager # new
from modules.window_lock import AspectRatioLock # new

def letterbox_frame(frame, target_w, target_h):
    """
    Resizes 'frame' to fit inside a (target_w x target_h) window while
    preserving its original aspect ratio. Adds black bars on whichever
    side is needed instead of stretching/squishing the content.
    """

    h, w = frame.shape[:2]

    src_aspect = w / h
    target_aspect = target_w / target_h

    if target_aspect > src_aspect:
        new_h = target_h
        new_w = int(new_h * src_aspect)
    else:
        new_w = target_w
        new_h = int(new_w / src_aspect)

    resized = cv2.resize(frame, (new_w, new_h))

    canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)

    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2

    canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

    return canvas

def main():

    # =============================
    # INITIALIZATION
    # =============================

    detector = HandDetector()

    renderer = Renderer()

    motion = MotionEngine()

    gesture = GestureRecognizer()

    mouse = MouseController()

    context_manager = SmartContextManager()

    ui = UI()

    worker = BackgroundWorker()

    counter = GestureCounter()

    pose_detector = PoseDetector()

    entertainment = EntertainmentMode(pose_detector)

    shot_manager = ScreenshotManager(worker, mouse)

    scroll_manager = ScrollManager(mouse)
    
    # =============================
    # MODE SYSTEM
    # =============================

    menu = ModeMenu()

    mode_controller = ModeController()

    menu_active = True

    current_mode = None

    back_timer = None

    palm_cooldown = 0

    previous_time = time.time()

    screenshot_hold_start = None
    SCREENSHOT_HOLD_TIME = 0.5

    window_name = "Gesture Control Experience"

    FIXED_WIDTH = 1280
    FIXED_HEIGHT = 720

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, FIXED_WIDTH, FIXED_HEIGHT)

    # The native OS window must actually exist before we can find its
    # handle, so force one frame through before hooking it.
    cv2.imshow(window_name, np.zeros((FIXED_HEIGHT, FIXED_WIDTH, 3), dtype=np.uint8))
    cv2.waitKey(1)

    aspect_lock = AspectRatioLock(window_name, FIXED_WIDTH, FIXED_HEIGHT)

    # =============================
    # MAIN LOOP
    # =============================

    while True:

        success, frame = detector.cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        timestamp = int(time.time() * 1000)

        # =============================
        # HAND DETECTION
        # =============================

        hand = None

        finger_count = 0

        confidence = 0

        if menu_active or current_mode in [0, 1]:

            results = detector.detect(frame, timestamp)

            if results and results.hand_landmarks:

                hand = motion.smooth(
                    results.hand_landmarks[0]
                )

                finger_count = counter.count_fingers(
                    hand
                )

                # Pull the model's real detection confidence for this hand
                if results.handedness:
                    confidence = results.handedness[0][0].score * 100
        # =============================
        # MENU
        # =============================

        if menu_active:

            selected = menu.draw(frame, finger_count)

            if selected is not None:

                current_mode = selected

                mode_controller.set_mode(current_mode)

                if current_mode == 1:
                    entertainment.reset()

                menu_active = False
                previous_time = time.time()

                print("MODE SELECTED:", current_mode)

            mode_controller.draw(frame)

            # cv2.imshow(window_name, frame)  # replace

            win_rect = cv2.getWindowImageRect(window_name)
            win_w, win_h = win_rect[2], win_rect[3]

            if win_w > 0 and win_h > 0:
                display_frame = letterbox_frame(frame, win_w, win_h)
            else:
                display_frame = frame

            cv2.imshow(window_name, display_frame)            

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            continue

        # =============================
        # ENTERTAINMENT MODE
        # =============================

        if current_mode == 1:

            entertainment.update(frame, timestamp)

            command = entertainment.get_command()

            if command == "RETRY":

                print("RESTARTING BOXING")

                entertainment.reset()

            elif command == "EXIT":

                print("EXITING ENTERTAINMENT")

                menu_active = True

                current_mode = None

                mode_controller.set_mode(None)

                entertainment.reset()

        # =============================
        # OPEN PALM RETURN
        # =============================

        if hand is not None:

            if finger_count == 5 and time.time() > palm_cooldown:

                if back_timer is None:
                    back_timer = time.time()

                elapsed = time.time() - back_timer

                cv2.putText(
                    frame,
                    f"MENU RETURN {2-int(elapsed)}",
                    (400, 100),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1.5,
                    (0, 255, 255),
                    3,
                )

                if elapsed >= 2:

                    print("RETURNING TO MENU")

                    menu_active = True

                    current_mode = None

                    mode_controller.set_mode(None)

                    entertainment.reset()

                    back_timer = None

                    palm_cooldown = time.time() + 2

            else:

                back_timer = None

            # =============================
            # DRAW HAND
            # =============================

            if current_mode != 1:
                renderer.draw_hand(frame, hand)

            # =============================
            # PROFESSIONAL MODE
            # =============================
            if current_mode == 0:

                gesture_name = gesture.recognize(hand)

                handled = context_manager.intercept(gesture_name, hand)

                if handled:

                    screenshot_hold_start = None

                else:

                    is_scroll = (gesture_name == "SCROLL")

                    scroll_manager.update(is_scroll, hand)

                    if gesture_name == "CURSOR":

                        mouse.move(hand)

                    elif gesture_name == "PINCH":

                        mouse.click()

                    elif gesture_name == "DOUBLE_CLICK":

                        mouse.double_click()

                    elif gesture_name == "RIGHT_CLICK":

                        mouse.right_click()

                    elif gesture_name == "DRAG":

                        mouse.drag()
                        mouse.move(hand)

                    elif gesture_name == "SCROLL":

                        pass  # already handled above by scroll_manager.update()

                    elif gesture_name == "SCREENSHOT":

                        if screenshot_hold_start is None:

                            screenshot_hold_start = time.time()

                        elif (
                            time.time() - screenshot_hold_start
                            >= SCREENSHOT_HOLD_TIME
                        ):

                            shot_manager.trigger()

                    else:

                        screenshot_hold_start = None
                        mouse.release()

                cv2.putText(
                    frame,
                    f"CONTEXT: {context_manager.current_profile}",
                    (20, 70),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.8,
                    (0, 200, 255),
                    2,
                )

            else:

                mouse.release()

        else:

            screenshot_hold_start = None
            mouse.release()

            back_timer = None
        # =============================
        # FPS
        # =============================

        current = time.time()

        fps = 1 / (current - previous_time)

        previous_time = current

        # =============================
        # SCREENSHOT
        # =============================

        shot_manager.update()

        if shot_manager.state == ScreenshotState.COUNTDOWN:

            cv2.putText(
                frame,
                str(shot_manager.current_countdown_value),
                (frame.shape[1] // 2 - 25, frame.shape[0] // 2 ),
                cv2.FONT_HERSHEY_DUPLEX,
                4,
                (0, 255, 255),
                6,
            )
        elif shot_manager.state == ScreenshotState.NOTIFICATION:
            cv2.putText(
                frame,
                "CAPTURING SCREENSHOT...",
               (frame.shape[1] // 2 - 180, 80),
                cv2.FONT_HERSHEY_DUPLEX,
                1.2,
                (0, 255, 0),
                3,
            )

        # =============================
        # UI
        # =============================

        if current_mode == 0:

            ui.draw(
                frame,
                fps,
                gesture_name,
                confidence,
                "PROFESSIONAL",
            )

        elif current_mode == 2:

            cv2.putText(
                frame,
                "AR MODE",
                (20, 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (255, 0, 255),
                2,
            )

        # cv2.imshow(window_name, frame)  # replace

        win_rect = cv2.getWindowImageRect(window_name)
        win_w, win_h = win_rect[2], win_rect[3]

        if win_w > 0 and win_h > 0:
            display_frame = letterbox_frame(frame, win_w, win_h)
        else:
            display_frame = frame

        cv2.imshow(window_name, display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # =============================
    # CLEAN EXIT
    # =============================

    mouse.stop()

    worker.stop()

    detector.release()

    pose_detector.release()

    aspect_lock.unhook()
    cv2.destroyAllWindows()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()