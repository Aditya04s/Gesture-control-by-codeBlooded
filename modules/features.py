"""
features.py
-----------------------
Feature Extraction Engine

Extracts useful information from
MediaPipe hand landmarks.

Author: Shane
"""

import math


class HandFeatures:

    def __init__(self, landmarks):

        self.landmarks = landmarks

        self.hand_size = self.calculate_hand_size()

        self.palm_center = self.calculate_palm_center()

        self.pinch_distance = self.distance(4, 8)

        self.middle_pinch = self.distance(4, 12)


    # ---------------------------------
    # Distance between two landmarks
    # ---------------------------------

    def distance(self, a, b):

        p1 = self.landmarks[a]
        p2 = self.landmarks[b]

        return math.sqrt(

            (p1.x - p2.x) ** 2 +

            (p1.y - p2.y) ** 2

        )


    # ---------------------------------
    # Hand Size
    # ---------------------------------

    def calculate_hand_size(self):

        return self.distance(
            0,
            9
        )


    # ---------------------------------
    # Palm Center
    # ---------------------------------

    def calculate_palm_center(self):

        x = 0
        y = 0

        palm = [0, 1, 5, 9, 13, 17]

        for i in palm:

            x += self.landmarks[i].x
            y += self.landmarks[i].y

        x /= len(palm)
        y /= len(palm)

        return (x, y)