"""
challenge.py
------------------------------------------
AI Gesture Experience

Visitor Challenge System

Author: Shane
"""

import random
import time


class VisitorChallenge:

    def __init__(self):

        self.gestures = [
            "OPEN PALM",
            "FIST",
            "PEACE",
            "THUMBS UP"
        ]

        self.current = random.choice(self.gestures)

        self.score = 0

        self.last_change = time.time()

        self.interval = 8

    def update(self, detected_gesture):

        now = time.time()

        if detected_gesture == self.current:

            self.score += 1

            self.current = random.choice(self.gestures)

            self.last_change = now

        elif now - self.last_change > self.interval:

            self.current = random.choice(self.gestures)

            self.last_change = now

    def get_target(self):

        return self.current

    def get_score(self):

        return self.score