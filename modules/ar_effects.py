import cv2
import math
import random


class AREffects:


    def __init__(self):

        self.mode = "LIGHTSABER"


    def draw_lightsaber(self, frame, hand_landmarks):

        if not hand_landmarks:
            return frame


        # MediaPipe hand points
        wrist = hand_landmarks[0]
        index_tip = hand_landmarks[8]


        h, w, _ = frame.shape


        x1 = int(wrist.x * w)
        y1 = int(wrist.y * h)

        x2 = int(index_tip.x * w)
        y2 = int(index_tip.y * h)


        # Extend the sword direction
        dx = x2 - x1
        dy = y2 - y1


        length = 250

        end_x = int(x2 + dx * length / max(abs(dx), 1))
        end_y = int(y2 + dy * length / max(abs(dy), 1))


        # Glow layers
        cv2.line(
            frame,
            (x2,y2),
            (end_x,end_y),
            (255,255,255),
            12
        )

        cv2.line(
            frame,
            (x2,y2),
            (end_x,end_y),
            (255,0,0),
            6
        )


        return frame