"""
modes/entertainment.py
---------------------------------
AI Gesture Experience

Entertainment Mode

Features
- MediaPipe Pose Tracking
- Full Body Skeleton
- Boxing Game
- Countdown
- Professional Boxing HUD (power/accuracy meters, punch type, combo)
- AI Coach voice feedback
- Hit Effects (normal / bonus / decoy)
- End Screen with full performance summary

Author: Shane
"""

import cv2
import time
import math

from modules.games.boxing import BoxingGame
from modules.audio import AudioManager


class EntertainmentMode:

    def __init__(self, pose_detector):

        self.pose_detector = pose_detector

        self.boxing = BoxingGame()

        self.audio = AudioManager()

        self.previous_state = "WAITING"

        # Hit effect

        self.hit_text = ""

        self.hit_start = 0

        self.hit_x = 640

        self.hit_y = 360

        self.hit_color = (0, 255, 0)

        self.last_score = 0

        self.command = None

        # Combo pop animation

        self.combo_pop_start = 0

        self.last_combo = 0

        # AI coach

        self.coach_text = ""

        self.coach_start = 0

        self.coach_duration = 1.8

        self.last_max_combo_announced = 0

        # =============================
        # AUDIO
        # =============================

    def handle_audio(self, state):

        if state == "INTRO":

            self.audio.play_music("boxing_bgm.wav")

        elif state == "COUNTDOWN":

            self.audio.play("countdown")

        elif state == "FIGHT":

            self.audio.stop_music()

            self.audio.play("bell")

        elif state == "FINISHED":

            self.audio.stop_music()

    # =============================
    # RESET
    # =============================

    def reset(self):

        self.boxing = BoxingGame()

        self.previous_state = "WAITING"

        self.hit_text = ""

        self.hit_start = 0

        self.hit_x = 640

        self.hit_y = 360

        self.hit_color = (0, 255, 0)

        self.last_score = 0

        self.command = None

        self.combo_pop_start = 0

        self.last_combo = 0

        self.coach_text = ""

        self.coach_start = 0

        self.last_max_combo_announced = 0

    # =============================
    # AI COACH
    # =============================

    def trigger_coach(self, text, sound=None):

        self.coach_text = text

        self.coach_start = time.time()

        if sound is not None:

            self.audio.play_sound(sound)

    def update_coach(self, status):

        # Combo milestones
        if status["combo"] > self.last_max_combo_announced and status["combo"] % 5 == 0 and status["combo"] > 0:

            self.last_max_combo_announced = status["combo"]

            self.trigger_coach(f"{status['combo']} COMBO! KEEP GOING", sound="success")

        # Bonus hit encouragement
        if status.get("last_hit_was_bonus") and status["hit"]:

            self.trigger_coach("BONUS HIT! NICE TIMING", sound="success")

        # Decoy punish
        if status.get("last_hit_was_decoy"):

            self.trigger_coach("THAT WAS A DECOY! STAY FOCUSED", sound="error")

    # =============================
    # HIT EFFECT
    # =============================

    def check_hit_effect(self, status):

        if status["score"] > self.last_score:

            if status.get("last_hit_was_bonus"):

                self.hit_text = "BONUS!"

                self.hit_color = (0, 215, 255)

            else:

                self.hit_text = "HIT!"

                self.hit_color = (0, 255, 0)

            self.hit_start = time.time()

            target = status["target"]

            if target:

                self.hit_x = int(target["x"])

                self.hit_y = int(target["y"])

            self.last_score = status["score"]

            self.audio.play_sound("punch")

        if status["combo"] != self.last_combo:

            if status["combo"] > self.last_combo:

                self.combo_pop_start = time.time()

            self.last_combo = status["combo"]

    # =============================
    # DRAW METER (generic horizontal bar)
    # =============================

    def draw_meter(self, frame, x, y, w, h, value, max_value, color, label):

        ratio = 0

        if max_value > 0:

            ratio = max(0, min(value / max_value, 1))

        cv2.rectangle(frame, (x, y), (x + w, y + h), (60, 60, 60), -1)

        cv2.rectangle(frame, (x, y), (x + int(w * ratio), y + h), color, -1)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 1)

        cv2.putText(
            frame,
            label,
            (x, y - 6),
            cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

    # =============================
    # END SCREEN
    # =============================

    def draw_end_screen(self, frame, status):

        overlay = frame.copy()

        cv2.rectangle(overlay, (120, 60), (1160, 660), (20, 20, 20), -1)

        frame[:] = cv2.addWeighted(overlay, 0.80, frame, 0.20, 0)

        cv2.putText(
            frame,
            "ROUND COMPLETE",
            (300, 140),
            cv2.FONT_HERSHEY_DUPLEX,
            2,
            (0, 255, 255),
            4,
        )

        cv2.putText(
            frame,
            f"FINAL SCORE : {status['final_score']}",
            (320, 210),
            cv2.FONT_HERSHEY_DUPLEX,
            1.3,
            (255, 255, 255),
            3,
        )

        cv2.putText(
            frame,
            f"BEST SCORE : {status['best_score']}",
            (320, 255),
            cv2.FONT_HERSHEY_DUPLEX,
            1.1,
            (0, 255, 0),
            3,
        )

        # Performance summary block

        stats_x = 320
        stats_y = 320
        line_gap = 40

        cv2.putText(
            frame,
            "PERFORMANCE SUMMARY",
            (stats_x, stats_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            (0, 255, 255),
            2,
        )

        stats_y += line_gap

        cv2.putText(
            frame,
            f"Accuracy : {status['accuracy']}%   ({status['total_hits']}/{status['total_punches']} punches)",
            (stats_x, stats_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.75,
            (255, 255, 255),
            2,
        )

        stats_y += line_gap

        cv2.putText(
            frame,
            f"Max Combo : x{status['max_combo']}",
            (stats_x, stats_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.75,
            (255, 255, 255),
            2,
        )

        stats_y += line_gap

        types = status["punch_types"]

        type_line = (
            f"Jab {types.get('JAB', 0)}  |  "
            f"Cross {types.get('CROSS', 0)}  |  "
            f"Hook {types.get('HOOK', 0)}  |  "
            f"Uppercut {types.get('UPPERCUT', 0)}"
        )

        cv2.putText(
            frame,
            type_line,
            (stats_x, stats_y),
            cv2.FONT_HERSHEY_DUPLEX,
            0.65,
            (200, 200, 200),
            2,
        )

    # =============================
    # UPDATE
    # =============================

    def update(self, frame, timestamp):

        pose_results = self.pose_detector.detect(frame, timestamp)

        if pose_results is not None and pose_results.pose_landmarks:

            self.pose_detector.draw(frame)

        self.boxing.update(pose_results)

        status = self.boxing.get_status()

        if status["state"] != self.previous_state:

            self.handle_audio(status["state"])

            self.previous_state = status["state"]

        self.check_hit_effect(status)

        self.update_coach(status)

        # =============================
        # MAIN TITLE
        # =============================

        cv2.putText(
            frame,
            "AI BOXING CHALLENGE",
            (20, 40),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (0, 255, 255),
            2,
        )

        # =============================
        # SCORE / COMBO HUD
        # =============================

        cv2.putText(
            frame,
            f"SCORE : {status['score']}",
            (20, 130),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 255, 255),
            2,
        )

        combo_scale = 1.0

        if time.time() - self.combo_pop_start < 0.25:

            combo_scale = 1.4

        cv2.putText(
            frame,
            f"COMBO : x{status['combo']}",
            (20, 170),
            cv2.FONT_HERSHEY_DUPLEX,
            combo_scale,
            (0, 255, 0),
            2,
        )

        # =============================
        # ACCURACY + POWER METERS
        # =============================

        self.draw_meter(
            frame,
            20, 210, 220, 18,
            status["accuracy"], 100,
            (0, 200, 255),
            f"ACCURACY {status['accuracy']}%",
        )

        last_punch = status.get("last_punch")

        power_value = last_punch["power"] if last_punch else 0

        self.draw_meter(
            frame,
            20, 260, 220, 18,
            power_value, 100,
            (0, 0, 255),
            f"POWER {power_value}",
        )

        if last_punch:

            cv2.putText(
                frame,
                f"LAST PUNCH: {last_punch['type']} ({last_punch['hand']})",
                (20, 310),
                cv2.FONT_HERSHEY_DUPLEX,
                0.65,
                (255, 255, 255),
                2,
            )

        # Live debug readout — remove this block once you've tuned
        # min_punch_speed_ratio in boxing.py and don't need it anymore.
        speed_now = status.get("last_measured_speed", 0.0)
        threshold = status.get("punch_threshold", 0.0)

        debug_color = (0, 255, 0) if speed_now > threshold else (180, 180, 180)

        cv2.putText(
            frame,
            f"speed: {speed_now:.2f} / threshold: {threshold:.2f}",
            (20, 335),
            cv2.FONT_HERSHEY_DUPLEX,
            0.5,
            debug_color,
            1,
        )

        # =============================
        # COUNTDOWN
        # =============================

        if status["state"] == "COUNTDOWN":

            cv2.putText(
                frame,
                str(status["countdown"]),
                (560, 350),
                cv2.FONT_HERSHEY_DUPLEX,
                6,
                (0, 0, 255),
                10,
            )

        # =============================
        # FIGHT MODE
        # =============================

        if status["state"] == "FIGHT":

            cv2.putText(
                frame,
                f"ROUND TIME : {status['time']}s",
                (430, 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (0, 255, 255),
                2,
            )

            target = status["target"]

            if target:

                pulse = int(target["radius"] + 12 * math.sin(time.time() * 5))

                x = int(target["x"])

                y = int(target["y"])

                target_type = target.get("type", "NORMAL")

                if target_type == "BONUS":

                    color = (0, 215, 255)

                    label = "BONUS!"

                elif target_type == "DECOY":

                    color = (80, 80, 255)

                    label = "AVOID!"

                else:

                    color = (0, 0, 255)

                    label = "PUNCH!"

                cv2.circle(frame, (x, y), pulse, color, -1)

                cv2.circle(frame, (x, y), pulse + 10, (255, 255, 255), 3)

                cv2.putText(
                    frame,
                    label,
                    (x - 60, y - int(pulse) - 20),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )

        elif status["state"] == "FINISHED":

            self.draw_end_screen(frame, status)

        # =============================
        # HIT EFFECT
        # =============================

        if time.time() - self.hit_start < 1:

            cv2.circle(frame, (self.hit_x, self.hit_y), 80, self.hit_color, 4)

            cv2.putText(
                frame,
                self.hit_text,
                (self.hit_x - 60, self.hit_y - 90),
                cv2.FONT_HERSHEY_DUPLEX,
                1.5,
                self.hit_color,
                3,
            )

        # =============================
        # AI COACH BANNER
        # =============================

        if self.coach_text and (time.time() - self.coach_start < self.coach_duration):

            text_size = cv2.getTextSize(
                self.coach_text, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2
            )[0]

            banner_x = 640 - text_size[0] // 2

            cv2.putText(
                frame,
                self.coach_text,
                (banner_x, 620),
                cv2.FONT_HERSHEY_DUPLEX,
                0.9,
                (0, 255, 255),
                2,
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
    # RELEASE
    # =============================

    def release(self):

        if hasattr(self.pose_detector, "release"):

            self.pose_detector.release()

        if hasattr(self.audio, "stop_music"):

            self.audio.stop_music()