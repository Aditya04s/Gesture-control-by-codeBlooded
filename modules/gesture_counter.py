"""
gesture_counter.py
-----------------------------
Counts raised fingers using MediaPipe Hand Landmarks.

Thumb is intentionally excluded from the count — thumb position
depends on left/right (sideways) geometry, which flips depending on
whether the palm or the back of the hand faces the camera. Index,
middle, ring, and pinky only need an up/down (bent vs straight)
check, which stays reliable in both orientations.

Supports:
- 0 = Fist
- 1 = Index
- 2 = Peace (Index + Middle)
- 3 = Three fingers (Index + Middle + Ring)
- 4 = Four fingers (Index + Middle + Ring + Pinky)

Author: Shane
"""

import math


class GestureCounter:

    # =============================
    # HAND ORIENTATION
    # =============================

    def orientation_value(self, landmarks):
        """
        Returns a signed value whose sign flips depending on whether
        the palm or the back of the hand faces the camera. Uses the
        2D cross product of (wrist -> index MCP) and (wrist -> pinky MCP),
        which mirrors correctly regardless of left/right hand.
        """

        wrist = landmarks[0]
        index_mcp = landmarks[5]
        pinky_mcp = landmarks[17]

        v1x = index_mcp.x - wrist.x
        v1y = index_mcp.y - wrist.y

        v2x = pinky_mcp.x - wrist.x
        v2y = pinky_mcp.y - wrist.y

        return (v1x * v2y) - (v1y * v2x)

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