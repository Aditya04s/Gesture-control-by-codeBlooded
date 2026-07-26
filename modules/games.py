"""
games.py
------------------------------------------
AI Gesture Experience

Mini Games Engine

Author: Shane
"""

import cv2
import random
import math


class MiniGames:

    def __init__(self):

        self.target = None
        self.score = 0
        self.radius = 40

        self.new_target(1280, 720)

    def new_target(self, width, height):

        self.target = (

            random.randint(100, width - 100),

            random.randint(100, height - 100)

        )

    def aim_challenge(self, frame, hand):

        h, w = frame.shape[:2]

        if self.target is None:

            self.new_target(w, h)

        tx, ty = self.target

        ix = int(hand[8].x * w)
        iy = int(hand[8].y * h)

        cv2.circle(
            frame,
            (tx, ty),
            self.radius,
            (0, 255, 255),
            3
        )

        cv2.circle(
            frame,
            (ix, iy),
            10,
            (0, 255, 0),
            -1
        )

        cv2.line(
            frame,
            (ix, iy),
            (tx, ty),
            (255, 255, 255),
            1
        )

        distance = math.sqrt(

            (ix - tx) ** 2 +

            (iy - ty) ** 2

        )

        if distance < self.radius:

            self.score += 1

            self.new_target(w, h)

        cv2.putText(

            frame,

            f"Score : {self.score}",

            (20, frame.shape[0] - 20),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (0, 255, 0),

            2

        )

        return self.score