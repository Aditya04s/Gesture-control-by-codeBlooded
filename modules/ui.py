"""
ui.py
---------------------------------
Modern HUD

Author: Shane
"""

import cv2
import math


class UI:

    def __init__(self):

        self.angle = 0

    def draw(self, frame, fps, gesture, confidence, mode):

        h, w = frame.shape[:2]

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (15, 15),
            (420, 180),
            (25, 25, 25),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.55,
            frame,
            0.45,
            0,
            frame
        )

        cv2.putText(
            frame,
            "AI GESTURE EXPERIENCE",
            (30, 45),
            cv2.FONT_HERSHEY_DUPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"FPS : {int(fps)}",
            (30, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Gesture : {gesture}",
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Confidence : {int(confidence)}%",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Mode : {mode}",
            (30, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 180, 0),
            2
        )

        self.angle += 4

        radius = 25

        x = int(w - 60 + radius * math.cos(math.radians(self.angle)))
        y = int(60 + radius * math.sin(math.radians(self.angle)))

        cv2.circle(frame, (w - 60, 60), 30, (255, 255, 255), 2)
        cv2.circle(frame, (x, y), 6, (0, 255, 255), -1)