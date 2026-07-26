"""
gesture_counter.py
-----------------------------
Counts raised fingers using MediaPipe Hand Landmarks.

Supports:
- 0 = Fist
- 1 = Index
- 2 = Peace
- 3 = Three fingers
- 4 = Four fingers
- 5 = Open palm

Author: Shane
"""

import math


class GestureCounter:


    def __init__(self):

        pass



    # =============================
    # DISTANCE
    # =============================

    def distance(self, a, b):

        return math.sqrt(
            (a.x - b.x) ** 2 +
            (a.y - b.y) ** 2
        )



    # =============================
    # COUNT FINGERS
    # =============================

    def count_fingers(self, landmarks):


        count = 0



        # =============================
        # THUMB
        # =============================

        # Thumb opens sideways
        # Works for mirrored webcam view

        if landmarks[4].x > landmarks[3].x:

            count += 1



        # =============================
        # INDEX
        # =============================

        if landmarks[8].y < landmarks[6].y:

            count += 1



        # =============================
        # MIDDLE
        # =============================

        if landmarks[12].y < landmarks[10].y:

            count += 1



        # =============================
        # RING
        # =============================

        if landmarks[16].y < landmarks[14].y:

            count += 1



        # =============================
        # PINKY
        # =============================

        if landmarks[20].y < landmarks[18].y:

            count += 1



        return count