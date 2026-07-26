"""
modules/screenshot.py
---------------------------------
Screenshot State Machine Manager
"""

from enum import Enum, auto
import time


class ScreenshotState(Enum):
    IDLE = auto()
    COUNTDOWN = auto()
    CAPTURING = auto()
    NOTIFICATION = auto()


class ScreenshotManager:
    def __init__(self, worker_module, mouse_module):
        self.state = ScreenshotState.IDLE
        self.worker = worker_module
        self.mouse = mouse_module

        # State Timers
        self.state_start_time = 0
        self.countdown_duration = 3.0
        self.notification_duration = 2.0
        self.cooldown_duration = 3.0

        # Global tracking variables
        self.last_screenshot_time = 0
        self.current_countdown_value = 3

    def trigger(self):
        """Attempts to start a screenshot sequence from the main loop."""
        current_time = time.time()

        # Prevent starting a new screenshot if we are already in progress or in cooldown
        if self.state == ScreenshotState.IDLE:
            if current_time - self.last_screenshot_time >= self.cooldown_duration:
                self._transition_to(ScreenshotState.COUNTDOWN)

    def update(self):
        """
        Processes time-based state transitions.
        Called exactly once per frame inside the main loop.
        """
        if self.state == ScreenshotState.IDLE:
            return

        current_time = time.time()
        elapsed = current_time - self.state_start_time

        # 1. Handle Countdown State
        if self.state == ScreenshotState.COUNTDOWN:
            remaining = self.countdown_duration - elapsed

            if remaining > 0:
                self.current_countdown_value = int(remaining) + 1
            else:
                self._transition_to(ScreenshotState.CAPTURING)

        # 2. Handle Capturing State
        elif self.state == ScreenshotState.CAPTURING:
            self.worker.add_task("Disk_IO_Screenshot", self.mouse.screenshot)
            self.last_screenshot_time = time.time()
            self._transition_to(ScreenshotState.NOTIFICATION)

        # 3. Handle Notification State
        elif self.state == ScreenshotState.NOTIFICATION:
            if elapsed >= self.notification_duration:
                self._transition_to(ScreenshotState.IDLE)

    def _transition_to(self, next_state):
        """Internal helper to log transitions and reset state timers safely."""
        self.state = next_state
        self.state_start_time = time.time()