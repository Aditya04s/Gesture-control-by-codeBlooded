"""
modules/pose.py
---------------------------------
AI Gesture Experience

MediaPipe Tasks Pose Detector

Includes One Euro Filter smoothing on all landmarks: stays smooth
during small idle jitter (guard stance, standing still) but loosens
up automatically during fast motion (punches) so speed/power readings
don't lag behind the real movement.

Author: Shane
"""

import math

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# =============================
# ONE EURO FILTER
# =============================

class OneEuroFilter:
    """
    Adaptive low-pass filter (Casiez et al.). Smooths out small jitter
    at low speed, but automatically reduces lag at high speed — ideal
    for pose landmarks that need to sit still during a guard stance
    but track tightly during a fast punch.
    """

    def __init__(self, min_cutoff=1.0, beta=0.4, d_cutoff=1.0):

        # Higher min_cutoff = less smoothing / less lag at low speed
        self.min_cutoff = min_cutoff

        # Higher beta = filter loosens up more aggressively as speed
        # increases (more responsive to fast punches)
        self.beta = beta

        self.d_cutoff = d_cutoff

        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def _alpha(self, cutoff, dt):

        tau = 1.0 / (2 * math.pi * cutoff)

        return 1.0 / (1.0 + tau / dt)

    def filter(self, x, t):

        if self.t_prev is None:

            self.x_prev = x
            self.dx_prev = 0.0
            self.t_prev = t

            return x

        dt = max(t - self.t_prev, 1e-6)

        dx = (x - self.x_prev) / dt

        a_d = self._alpha(self.d_cutoff, dt)

        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)

        a = self._alpha(cutoff, dt)

        x_hat = a * x + (1 - a) * self.x_prev

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat

    def reset(self):

        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None


class PoseDetector:

    def __init__(self):

        model_path = "models/pose_landmarker.task"

        base_options = python.BaseOptions(
            model_asset_path=model_path
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.6,
            min_tracking_confidence=0.7
        )

        self.detector = vision.PoseLandmarker.create_from_options(options)

        self.results = None

        # =============================
        # SMOOTHING
        # =============================

        # Toggle to False to compare raw vs smoothed while tuning.
        self.enable_smoothing = True

        # TUNE THESE if smoothing feels laggy (raise min_cutoff / beta)
        # or still jittery (lower them). beta has the biggest effect
        # on how tightly punches get tracked.
        self.smoothing_min_cutoff = 1.0
        self.smoothing_beta = 0.4
        self.smoothing_d_cutoff = 1.0

        # One filter per (landmark index, coordinate)
        self.filters_x = {}
        self.filters_y = {}
        self.filters_z = {}

        self._init_filters()

        # Auto-reset filters if the player disappears for a while, so
        # a new player (or the same player stepping back in) doesn't
        # inherit stale velocity state and jump on the first frame.
        self.no_detection_count = 0
        self.no_detection_reset_threshold = 15

        # MediaPipe Pose Connections
        self.connections = [

            # Face
            (0,1),(1,2),(2,3),(3,7),
            (0,4),(4,5),(5,6),(6,8),

            # Shoulders
            (11,12),

            # Left Arm
            (11,13),
            (13,15),
            (15,17),
            (15,19),
            (15,21),
            (17,19),

            # Right Arm
            (12,14),
            (14,16),
            (16,18),
            (16,20),
            (16,22),
            (18,20),

            # Torso
            (11,23),
            (12,24),
            (23,24),

            # Left Leg
            (23,25),
            (25,27),
            (27,29),
            (29,31),

            # Right Leg
            (24,26),
            (26,28),
            (28,30),
            (30,32)
        ]

    # -----------------------------------
    # Filter setup / reset
    # -----------------------------------

    def _init_filters(self):

        self.filters_x = {}
        self.filters_y = {}
        self.filters_z = {}

        for i in range(33):

            self.filters_x[i] = OneEuroFilter(
                self.smoothing_min_cutoff,
                self.smoothing_beta,
                self.smoothing_d_cutoff,
            )

            self.filters_y[i] = OneEuroFilter(
                self.smoothing_min_cutoff,
                self.smoothing_beta,
                self.smoothing_d_cutoff,
            )

            self.filters_z[i] = OneEuroFilter(
                self.smoothing_min_cutoff,
                self.smoothing_beta,
                self.smoothing_d_cutoff,
            )

    def reset_filters(self):

        for i in range(33):

            self.filters_x[i].reset()
            self.filters_y[i].reset()
            self.filters_z[i].reset()

    # -----------------------------------
    # Apply smoothing to landmarks in place
    # -----------------------------------

    def _smooth_landmarks(self, landmarks, timestamp):

        # timestamp arrives in ms (video mode) — filter works in
        # seconds internally.
        t = timestamp / 1000.0

        for i, lm in enumerate(landmarks):

            if i not in self.filters_x:
                continue

            lm.x = self.filters_x[i].filter(lm.x, t)
            lm.y = self.filters_y[i].filter(lm.y, t)
            lm.z = self.filters_z[i].filter(lm.z, t)

    # -----------------------------------
    # Detect
    # -----------------------------------

    def detect(self, frame, timestamp):

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        self.results = self.detector.detect_for_video(
            mp_image,
            timestamp
        )

        if not self.results.pose_landmarks:

            self.no_detection_count += 1

            if self.no_detection_count >= self.no_detection_reset_threshold:

                self.reset_filters()
                self.no_detection_count = 0

            return self.results

        self.no_detection_count = 0

        if self.enable_smoothing:

            self._smooth_landmarks(
                self.results.pose_landmarks[0],
                timestamp
            )

        return self.results

    # -----------------------------------
    # Get Landmarks
    # -----------------------------------

    def get_landmarks(self):

        if self.results is None:
            return None

        if not self.results.pose_landmarks:
            return None

        return self.results.pose_landmarks[0]

    # -----------------------------------
    # Draw Skeleton
    # -----------------------------------

    def draw(self, frame):

        landmarks = self.get_landmarks()

        if landmarks is None:
            return

        h, w = frame.shape[:2]

        # Draw skeleton lines
        for start, end in self.connections:

            p1 = landmarks[start]
            p2 = landmarks[end]

            x1 = int(p1.x * w)
            y1 = int(p1.y * h)

            x2 = int(p2.x * w)
            y2 = int(p2.y * h)

            cv2.line(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 255),
                1,
                cv2.LINE_AA
            )

        # Draw joints
        for lm in landmarks:

            x = int(lm.x * w)
            y = int(lm.y * h)

            cv2.circle(
                frame,
                (x, y),
                3,
                (0, 255, 0),
                -1,
                cv2.LINE_AA
            )

    # -----------------------------------
    # Release
    # -----------------------------------

    def release(self):

        self.detector.close()