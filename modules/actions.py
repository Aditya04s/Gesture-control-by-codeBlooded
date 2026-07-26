"""
actions.py
---------------------------------
AI Gesture Experience v4.0

Action Manager

Author: Shane
"""

import time


class ActionManager:

    def __init__(self):

        self.current_mode = "NORMAL"

        self.last_action = ""

        self.cooldowns = {}

        self.cooldown_time = 1.0

    # ----------------------------
    # Cooldown
    # ----------------------------

    def can_execute(self, action):

        now = time.time()

        if action not in self.cooldowns:
            self.cooldowns[action] = 0

        if now - self.cooldowns[action] >= self.cooldown_time:

            self.cooldowns[action] = now
            return True

        return False

    # ----------------------------
    # Execute Action
    # ----------------------------

    def execute(self, gesture):

        action = "NONE"

        if gesture == "OPEN PALM":

            if self.can_execute("OPEN"):

                self.current_mode = "NORMAL"
                action = "Resume"

        elif gesture == "FIST":

            if self.can_execute("FIST"):

                self.current_mode = "PAUSE"
                action = "Paused"

        elif gesture == "PEACE":

            if self.can_execute("PEACE"):

                self.current_mode = "PRESENTATION"
                action = "Presentation Mode"

        elif gesture == "THUMBS UP":

            if self.can_execute("THUMBS"):

                action = "Thumbs Up"

        self.last_action = action

        return action