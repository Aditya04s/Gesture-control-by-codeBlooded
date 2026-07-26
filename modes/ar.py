"""
modes/ar.py
---------------------------------
AI Gesture Experience

Augmented Reality Mode

This module does NOT draw the AR effects itself. TouchDesigner does.
This module's job is: track the body, stream landmark coordinates and
an active/inactive signal to TouchDesigner over OSC, and show a small
local debug HUD so you can confirm tracking is working from the
Python window.

Requires: pip install python-osc

TouchDesigner side: add an "OSC In CHOP" listening on the same
osc_ip / osc_port as below, then reference channels like
/pose/left_wrist, /pose/right_wrist, /pose/nose, etc. to drive your
flying-animal network. /ar/active tells you when to show/hide them.

Author: Shane
"""

import cv2
import time

from pythonosc.udp_client import SimpleUDPClient


class ARMode:

    # Landmark indices (MediaPipe Pose) streamed to TouchDesigner.
    # Add more entries here (any of the 33 pose landmark indices) if
    # your TD network wants more tracking points.
    TRACKED_LANDMARKS = {
        "nose": 0,
        "left_shoulder": 11,
        "right_shoulder": 12,
        "left_wrist": 15,
        "right_wrist": 16,
        "left_hip": 23,
        "right_hip": 24,
    }

    def __init__(self, pose_detector, osc_ip="127.0.0.1", osc_port=7000):

        self.pose_detector = pose_detector

        # Point this at whatever IP/port your TouchDesigner "OSC In
        # CHOP" is listening on. 127.0.0.1:7000 is just a common local
        # default -- change it to match your TD patch.
        self.osc_ip = osc_ip
        self.osc_port = osc_port

        self.osc_client = SimpleUDPClient(osc_ip, osc_port)

        self.command = None

        self.active_sent = False

        self.last_send_time = 0

        # Cap OSC send rate -- plenty smooth for TD, keeps UDP traffic
        # light. Lower this (bigger number) if animals feel laggy,
        # raise the interval if your network/CPU is struggling.
        self.send_interval = 1.0 / 45.0

    # =============================
    # OSC SEND
    # =============================

    def send_active(self, active):

        try:

            self.osc_client.send_message("/ar/active", 1 if active else 0)

            self.active_sent = active

        except Exception as e:

            print("AR OSC send_active error:", e)

    def send_landmarks(self, landmarks):

        try:

            for name, idx in self.TRACKED_LANDMARKS.items():

                lm = landmarks[idx]

                self.osc_client.send_message(
                    f"/pose/{name}",
                    [float(lm.x), float(lm.y), float(lm.z)],
                )

            # Shoulder-width scale reference -- useful in TD to size
            # effects relative to how close the player is to the
            # camera.
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]

            shoulder_width = (
                (left_shoulder.x - right_shoulder.x) ** 2 +
                (left_shoulder.y - right_shoulder.y) ** 2
            ) ** 0.5

            self.osc_client.send_message("/pose/scale", float(shoulder_width))

        except Exception as e:

            print("AR OSC send_landmarks error:", e)

    # =============================
    # UPDATE
    # =============================

    def update(self, frame, timestamp):

        if not self.active_sent:

            self.send_active(True)

        pose_results = self.pose_detector.detect(frame, timestamp)

        has_pose = pose_results is not None and pose_results.pose_landmarks

        if has_pose:

            self.pose_detector.draw(frame)

            now = time.time()

            if now - self.last_send_time >= self.send_interval:

                self.send_landmarks(pose_results.pose_landmarks[0])

                self.last_send_time = now

        # =============================
        # LOCAL DEBUG HUD
        # (the real AR visuals render in TouchDesigner, not here)
        # =============================

        cv2.putText(
            frame,
            "AR MODE",
            (20, 40),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 0, 255),
            2,
        )

        status_text = "TRACKING" if has_pose else "NO BODY DETECTED"

        status_color = (0, 255, 0) if has_pose else (0, 0, 255)

        cv2.putText(
            frame,
            status_text,
            (20, 75),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            status_color,
            2,
        )

        cv2.putText(
            frame,
            f"-> OSC {self.osc_ip}:{self.osc_port}",
            (20, 105),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (200, 200, 200),
            1,
        )

        return frame

    # =============================
    # COMMAND
    # =============================

    def get_command(self):

        command = self.command

        self.command = None

        return command

    # =============================
    # RESET
    # =============================

    def reset(self):

        self.last_send_time = 0

        self.command = None

        # Re-announce active in case TD was restarted or missed it.
        self.send_active(True)

    # =============================
    # RELEASE
    # =============================

    def release(self):

        # NOTE: pose_detector is shared with EntertainmentMode and is
        # released once, centrally, in main.py's clean-exit section --
        # do not release it here, or you'll double-close it.

        self.send_active(False)