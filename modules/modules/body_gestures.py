"""
body_gestures.py
------------------------------------------
Body Gesture Recognition

Author: Shane
"""


import math


class BodyGestureRecognizer:

    def __init__(self):
        pass

    def distance(self, a, b):

        return math.sqrt(

            (a.x - b.x) ** 2 +

            (a.y - b.y) ** 2

        )

    def boxing_pose(self, pose):

        if len(pose) < 33:
            return False

        left_wrist = pose[15]
        right_wrist = pose[16]

        left_shoulder = pose[11]
        right_shoulder = pose[12]

        left_ok = (
            self.distance(
                left_wrist,
                left_shoulder
            ) < 0.22
        )

        right_ok = (
            self.distance(
                right_wrist,
                right_shoulder
            ) < 0.22
        )

        return left_ok and right_ok

    def hands_up(self, pose):

        if len(pose) < 33:
            return False

        left_wrist = pose[15]
        right_wrist = pose[16]

        nose = pose[0]

        return (
            left_wrist.y < nose.y and
            right_wrist.y < nose.y
        )

    def t_pose(self, pose):

        if len(pose) < 33:
            return False

        left = pose[15]
        right = pose[16]

        ls = pose[11]
        rs = pose[12]

        return (

            abs(left.y - ls.y) < 0.08 and

            abs(right.y - rs.y) < 0.08

        )

    def recognize(self, pose):

        if self.boxing_pose(pose):
            return "BOXING"

        if self.hands_up(pose):
            return "HANDS UP"

        if self.t_pose(pose):
            return "T-POSE"

        return "NONE"