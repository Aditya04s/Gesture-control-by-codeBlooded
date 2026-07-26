"""
mode_manager.py
-----------------------------
AI Gesture Experience

Handles application modes.

Author: Shane
"""

from enum import Enum


class Mode(Enum):
    PROFESSIONAL = 0
    ENTERTAINMENT = 1
    AR = 2


class ModeManager:

    def __init__(self):
        self.current_mode = Mode.PROFESSIONAL

    def set_mode(self, mode):
        self.current_mode = mode

    def get_mode(self):
        return self.current_mode

    def next_mode(self):
        modes = list(Mode)
        index = modes.index(self.current_mode)
        self.current_mode = modes[(index + 1) % len(modes)]

    def previous_mode(self):
        modes = list(Mode)
        index = modes.index(self.current_mode)
        self.current_mode = modes[(index - 1) % len(modes)]