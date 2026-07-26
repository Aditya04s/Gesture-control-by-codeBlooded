"""
modules/mouse.py
---------------------------------
Asynchronous Threaded Mouse Controller Engine
"""

import os
import threading
import time
import pyautogui

# Safety fallback configurations for PyAutoGUI automation
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0  # Wipes out default 0.1s UI locking lag completely!


class MouseController:
    def __init__(self):
        # Retrieve the monitor's pixel dimensions
        self.screen_w, self.screen_h = pyautogui.size()

        # NEW: Active Control Region (ACR) Configurations
        self.margin_x = 0.15  # 15% horizontal margin (Left & Right)
        self.margin_y = 0.15  # 15% vertical margin (Top & Bottom)

        # Thread communication variables
        self.target_x = None
        self.target_y = None
        self.is_dragging = False

        # Define and start the asynchronous movement worker loop
        self.running = True
        self.mouse_thread = threading.Thread(
            target=self._mouse_loop,
            daemon=True
        )
        self.mouse_thread.start()

    def move(self, hand_landmarks):
        """Calculates normalized screen coords within the ACR and updates target position."""
        index_tip = hand_landmarks[8]

        # 1. Define the active tracking boundaries (0.0 to 1.0 space)
        active_x_start = self.margin_x
        active_x_end = 1.0 - self.margin_x
        active_y_start = self.margin_y
        active_y_end = 1.0 - self.margin_y

        # 2. Normalize the coordinates strictly within the ACR
        mapped_x = (index_tip.x - active_x_start) / (active_x_end - active_x_start)
        mapped_y = (index_tip.y - active_y_start) / (active_y_end - active_y_start)

        # 3. Clamp values to prevent overshooting the screen edges
        mapped_x = max(0.0, min(1.0, mapped_x))
        mapped_y = max(0.0, min(1.0, mapped_y))

        # 4. Map directly to absolute screen pixels
        self.target_x = int(mapped_x * self.screen_w)
        self.target_y = int(mapped_y * self.screen_h)

    def click(self):
        """Triggers a virtual primary click."""
        if self.target_x is not None and self.target_y is not None:
            pyautogui.click(self.target_x, self.target_y)

    def double_click(self):
        """Triggers a rapid double-click."""
        if self.target_x is not None and self.target_y is not None:
            pyautogui.doubleClick(self.target_x, self.target_y)

    def drag(self):
        """Fires the OS mouse-down event once to initiate a drag."""
        if not self.is_dragging:
            self.is_dragging = True
            pyautogui.mouseDown(button="left")

    def drag_move(self, hand_landmarks):
        """Updates targeted coordinates while drag lock states stay active."""
        self.move(hand_landmarks)

    def release(self):
        """Fires the OS mouse-up event to release a drag lock safely."""
        if self.is_dragging:
            pyautogui.mouseUp(button="left")
            self.is_dragging = False

    def scroll(self, value):
        """Fires an instant hardware scroll interaction call."""
        pyautogui.scroll(value)

    def screenshot(self):
        """Captures and saves a timed disk stamp file securely."""

        # Create the screenshots folder automatically if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{timestamp}.png"

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        print(f"\n[Worker Asset] Screen saved asynchronously out to: {filename}")

    def _mouse_loop(self):
        """Internal worker thread loop prioritizing hardware position sync execution."""
        last_x, last_y = pyautogui.position()

        while self.running:
            if self.target_x is not None and self.target_y is not None:
                tx, ty = self.target_x, self.target_y

                if tx != last_x or ty != last_y:
                    # Because mouseDown is active, the OS automatically treats this as dragging
                    pyautogui.moveTo(tx, ty)
                    last_x, last_y = tx, ty

            time.sleep(0.008)

    def stop(self):
        """Stops the internal mouse driver execution thread safely."""
        self.running = False

        if self.mouse_thread.is_alive():
            self.mouse_thread.join(timeout=1.0)