"""
detector.py
---------------------------------
AI Gesture Experience

MediaPipe Tasks Hand Detector

Features:
- MediaPipe Tasks API ONLY
- Webcam handling
- Hand landmark detection
- Stable tracking
- Production path handling

Author: Shane
"""


import cv2
import mediapipe as mp
import os
import time


from mediapipe.tasks import python
from mediapipe.tasks.python import vision



class HandDetector:

<<<<<<< HEAD
    # =============================
    # CAMERA AUTO-SELECTION
    # =============================

    def _get_best_camera_index(self, max_devices=5):
        """
        Scans camera indices and returns the highest-numbered one
        that opens successfully. External USB webcams almost always
        enumerate after the built-in laptop camera (index 0), so the
        highest working index is treated as the external device.
=======
    def _get_best_camera_index(self, max_devices=5):
        """
        Scans camera indices and returns the highest one that opens.
        If only the built-in camera (index 0) exists, this returns 0 —
        identical to your current hardcoded behavior. If an external
        webcam is plugged in, it enumerates at a higher index and gets
        picked automatically instead.
>>>>>>> feature-gesture
        """

        available = []

        for i in range(max_devices):

<<<<<<< HEAD
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

            if cap.isOpened():
                available.append(i)
                cap.release()
=======
            cap = cv2.VideoCapture(i)

            if cap.isOpened():
                available.append(i)

            cap.release()
>>>>>>> feature-gesture

        if not available:
            return 0

        return max(available)

    def __init__(self):


        # =============================
        # MODEL PATH
        # =============================


        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )


        self.model_path = os.path.join(
            project_root,
            "models",
            "hand_landmarker.task"
        )



        if not os.path.exists(self.model_path):

            raise FileNotFoundError(
                f"Hand model not found:\n{self.model_path}"
            )



        # =============================
        # MEDIAPIPE HAND MODEL
        # =============================


        base_options = python.BaseOptions(
            model_asset_path=self.model_path
        )


        options = vision.HandLandmarkerOptions(

            base_options=base_options,

            num_hands=1,


            min_hand_detection_confidence=0.6,

            min_hand_presence_confidence=0.6,

            min_tracking_confidence=0.7,


            running_mode=vision.RunningMode.VIDEO

        )



        self.detector = vision.HandLandmarker.create_from_options(
            options
        )


        print(
            "[AI] Hand Landmarker loaded"
        )



        # =============================
        # CAMERA
        # =============================


<<<<<<< HEAD
        camera_index = self._get_best_camera_index()
=======
        # self.cap = cv2.VideoCapture(0) 

        camera_index = self._get_best_camera_index()

        self.cap = cv2.VideoCapture(camera_index)
>>>>>>> feature-gesture

        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        print(f"[Camera] Using camera index {camera_index}")


        if not self.cap.isOpened():

            raise RuntimeError(
                "Camera failed to open"
            )



        # Resolution

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            1280
        )


        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            720
        )



        # FPS

        self.cap.set(
            cv2.CAP_PROP_FPS,
            60
        )



        actual_width = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )


        actual_height = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )


        actual_fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )



        print(
            f"[Camera] {actual_width}x{actual_height} @ {actual_fps} FPS"
        )



        # =============================
        # DEBUG CONTROL
        # =============================


        self.last_detection = False

        self.last_print_time = 0





    # =============================
    # HAND DETECTION
    # =============================


    def detect(
        self,
        frame,
        timestamp
    ):


        # BGR -> RGB

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )



        mp_image = mp.Image(

            image_format=mp.ImageFormat.SRGB,

            data=rgb_frame

        )



        results = self.detector.detect_for_video(

            mp_image,

            timestamp

        )



        detected = bool(
            results.hand_landmarks
        )


<<<<<<< HEAD
=======

        # print once per second only

        # current_time = time.time()


        # if detected and current_time - self.last_print_time > 1:


        #     print(
        #         "[AI] Hand detected"
        #     )


        #     self.last_print_time = current_time



>>>>>>> feature-gesture
        self.last_detection = detected



        return results





    # =============================
    # RELEASE
    # =============================


    def release(self):


        if self.cap.isOpened():

            self.cap.release()



        self.detector.close()