"""
renderer.py
--------------------
AI Gesture Experience

Professional Hand Renderer

Author: Shane
"""

import cv2

# -----------------------------
# HAND CONNECTIONS
# -----------------------------
HAND_CONNECTIONS = [

    # Thumb
    (0,1),(1,2),(2,3),(3,4),

    # Index
    (0,5),(5,6),(6,7),(7,8),

    # Middle
    (0,9),(9,10),(10,11),(11,12),

    # Ring
    (0,13),(13,14),(14,15),(15,16),

    # Pinky
    (0,17),(17,18),(18,19),(19,20),

    # Palm
    (5,9),
    (9,13),
    (13,17)
]


class Renderer:

    def __init__(self):

        self.debug = False

    def draw_hand(self, frame, hand_landmarks):

        h, w, _ = frame.shape

        points = []

        # ---------------------------------
        # Convert landmarks to pixels
        # ---------------------------------
        for lm in hand_landmarks:

            x = int(lm.x * w)
            y = int(lm.y * h)

            points.append((x, y))

        # ---------------------------------
        # Draw Skeleton
        # ---------------------------------
        for start, end in HAND_CONNECTIONS:

            # Glow
            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 0, 120),
                4,
                cv2.LINE_AA
            )

            # Main line
            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

        # ---------------------------------
        # Draw All Joints
        # ---------------------------------
        for point in points:

            # Glow
            cv2.circle(
                frame,
                point,
                6,
                (0, 0, 120),
                -1,
                cv2.LINE_AA
            )

            # Core
            cv2.circle(
                frame,
                point,
                2,
                (0, 0, 255),
                -1,
                cv2.LINE_AA
            )

        # ---------------------------------
        # Debug Landmark Numbers
        # ---------------------------------
        if self.debug:

            for idx, point in enumerate(points):

                cv2.putText(
                    frame,
                    str(idx),
                    (point[0] + 6, point[1] - 6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )