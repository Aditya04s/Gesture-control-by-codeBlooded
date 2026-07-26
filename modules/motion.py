"""
motion.py
--------------------
Motion smoothing engine

Handles:
- Landmark smoothing
- Jitter reduction
- Stable tracking

Author: Shane
"""


class MotionEngine:

    def __init__(self, smoothing=0.6):

        # Previous landmark positions
        self.previous = None

        # Smoothing factor
        self.smoothing = smoothing


    def smooth(self, landmarks):

        """
        Apply exponential smoothing
        to hand landmarks.
        """

        if self.previous is None:

            self.previous = landmarks
            return landmarks


        smooth_landmarks = []


        for old, new in zip(
            self.previous,
            landmarks
        ):

            x = (
                old.x * self.smoothing
                +
                new.x * (1 - self.smoothing)
            )

            y = (
                old.y * self.smoothing
                +
                new.y * (1 - self.smoothing)
            )

            z = (
                old.z * self.smoothing
                +
                new.z * (1 - self.smoothing)
            )


            old.x = x
            old.y = y
            old.z = z


            smooth_landmarks.append(old)


        self.previous = smooth_landmarks


        return smooth_landmarks