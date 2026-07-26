"""
stability.py
--------------------
Gesture stability filter

Prevents accidental gesture triggers

Author: Shane
"""


from collections import deque


class GestureStability:


    def __init__(self, history_size=15):

        self.history = deque(
            maxlen=history_size
        )


        self.current_gesture = "NONE"



    def update(self, gesture):

        """
        Add latest gesture
        and return stable result
        """


        self.history.append(
            gesture
        )


        # Count occurrences

        count = self.history.count(
            gesture
        )


        confidence = (
            count /
            len(self.history)
        ) * 100



        # Need enough frames

        if confidence > 70:

            self.current_gesture = gesture


        return (
            self.current_gesture,
            confidence
        )