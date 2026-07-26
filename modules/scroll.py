"""
modules/scroll.py
---------------------------------
Infinite Relative Scroll Controller
"""

import time

class ScrollManager:
    def __init__(self, mouse_module):
        self.mouse = mouse_module
        self.is_active = False
        self.baseline_y = None
        self.last_exit_time = 0
        
        # Configuration Parameters
        self.cooldown_duration = 0.3  # Prevents flickering on drop-outs
        self.dead_zone = 0.015        # Normalized distance (ignores minor tremors)
        self.scroll_speed_multiplier = 3000

        # UI Feedback variables
        self.current_speed = 0
        self.direction = "-"

    def _get_palm_center_y(self, hand_landmarks):
        """Calculates the stable center of the palm using Wrist + MCP joints."""
        y_coords = [
            hand_landmarks[0].y,
            hand_landmarks[5].y,
            hand_landmarks[9].y,
            hand_landmarks[13].y,
            hand_landmarks[17].y
        ]
        return sum(y_coords) / len(y_coords)

    def update(self, is_scroll_gesture, hand_landmarks):
        """
        Processes infinite relative scrolling. 
        Runs every frame.
        """
        current_time = time.time()

        # 1. Exit Mode or Idle
        if not is_scroll_gesture:
            if self.is_active:
                self.is_active = False
                self.baseline_y = None
                self.last_exit_time = current_time
                self.current_speed = 0
                self.direction = "-"
            return

        # 2. Cooldown Check (Prevents rapid re-entry)
        if not self.is_active and (current_time - self.last_exit_time < self.cooldown_duration):
            return

        palm_y = self._get_palm_center_y(hand_landmarks)

        # 3. Enter Scroll Mode & Set Baseline
        if not self.is_active:
            self.is_active = True
            self.baseline_y = palm_y
            self.current_speed = 0
            return

        # 4. Compute Delta & Check Dead Zone
        delta_y = self.baseline_y - palm_y

        if abs(delta_y) > self.dead_zone:
            # Calculate exponential speed based on distance beyond the dead zone
            scroll_amount = int(delta_y * self.scroll_speed_multiplier)
            
            # Update UI Feedback
            self.current_speed = abs(scroll_amount)
            self.direction = "UP" if scroll_amount > 0 else "DOWN"

            # Trigger OS Scroll via Mouse Controller
            self.mouse.scroll(scroll_amount)
            
            # 5. Infinite Scroll Magic: Update baseline so movement continues seamlessly
            self.baseline_y = palm_y
        else:
            self.current_speed = 0
            self.direction = "-"