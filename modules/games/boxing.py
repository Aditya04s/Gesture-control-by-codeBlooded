"""
modules/games/boxing.py

AI Gesture Experience
Advanced Boxing Game Engine

Features:
- Guard detection (smoothed)
- Intro timer
- Countdown
- 60 second round
- Multi target system (normal / bonus / decoy)
- Advanced punch AI (jab / cross / hook / uppercut)
- Punch speed + power calculation (camera-distance normalized)
- Accuracy tracking
- Score + combo system
- Difficulty scaling
- Persistent high score
- Game over + full stat summary

Author: Shane
"""

import time
import math
import random
import json
import os


class BoxingGame:

    def __init__(self):

        self.state = "WAITING"

        # =============================
        # INTRO
        # =============================

        self.intro_start = None
        self.intro_duration = 14

        # =============================
        # COUNTDOWN
        # =============================

        self.countdown_start = None
        self.countdown_value = 3

        # =============================
        # ROUND TIMER
        # =============================

        self.round_start = None
        self.round_duration = 60

        self.final_score = 0

        # =============================
        # HIGH SCORE (PERSISTENT)
        # =============================

        self.highscore_path = os.path.join("data", "highscore.json")
        self.best_score = self.load_highscore()

        # =============================
        # SCORE / COMBO
        # =============================

        self.score = 0
        self.combo = 0
        self.max_combo = 0

        # =============================
        # PUNCH TRACKING (PER HAND)
        # =============================

        # Each hand gets its own independent history so a left and right
        # punch in the same frame are both detected instead of the second
        # one overwriting the first.
        self.hand_state = {
            "LEFT": {
                "last_wrist": None,
                "last_elbow": None,
                "last_shoulder": None,
                "last_sample_time": 0,
                "last_punch_time": 0,
                "extending": False,
                "start_wrist": None,
                "start_time": 0,
            },
            "RIGHT": {
                "last_wrist": None,
                "last_elbow": None,
                "last_shoulder": None,
                "last_sample_time": 0,
                "last_punch_time": 0,
                "extending": False,
                "start_wrist": None,
                "start_time": 0,
            },
        }

        self.punch_cooldown = 0.35

        # Minimum velocity to count as a real punch, measured in
        # shoulder-widths per second (distance / time, not raw
        # per-frame distance). This makes detection consistent
        # regardless of your pipeline's actual frame rate.
        # TUNE THIS: watch the live "speed" value shown on the HUD
        # while throwing real punches, and set this just below the
        # typical value of a real punch and above idle hand jitter.
        self.min_punch_speed_ratio = 3.0

        # Smallest time delta we'll divide by, to avoid a burst of
        # huge/false velocity readings if two frames land unusually
        # close together.
        self.min_dt = 1.0 / 60.0

        # =============================
        # ACCURACY TRACKING
        # =============================

        self.total_punches = 0
        self.total_hits = 0

        # Punch type breakdown, e.g. {"JAB": 4, "CROSS": 2, ...}
        self.punch_type_counts = {
            "JAB": 0,
            "CROSS": 0,
            "HOOK": 0,
            "UPPERCUT": 0,
        }

        self.last_punch_info = None

        # Live velocity reading (shoulder-widths/sec), updated every
        # frame a hand is tracked — even below the punch threshold.
        # Shown on the HUD so you can tune min_punch_speed_ratio by
        # watching real numbers instead of guessing.
        self.last_measured_speed = 0.0

        # =============================
        # GUARD DETECTION (SMOOTHED)
        # =============================

        self.guard_history = []
        self.guard_history_len = 6
        self.guard_confirm_ratio = 0.7

        # =============================
        # TARGET SYSTEM
        # =============================

        self.target = None

        self.base_target_radius = 80
        self.min_target_radius = 45

        self.last_target_move = time.time()
        self.base_target_move_delay = 2.5
        self.min_target_move_delay = 1.0

        # Frame bounds used for target placement (matches render resolution)
        self.frame_w = 1280
        self.frame_h = 720

        # =============================
        # FEEDBACK
        # =============================

        self.hit = False
        self.hit_time = 0
        self.last_hit_was_bonus = False
        self.last_hit_was_decoy = False

        # =============================
        # DIFFICULTY
        # =============================

        # 0.0 at round start -> 1.0 near round end
        self.difficulty = 0.0

    # =============================
    # HIGH SCORE PERSISTENCE
    # =============================

    def load_highscore(self):

        try:
            if os.path.exists(self.highscore_path):
                with open(self.highscore_path, "r") as f:
                    data = json.load(f)
                    return int(data.get("best_score", 0))
        except Exception:
            pass

        return 0

    def save_highscore(self):

        try:
            folder = os.path.dirname(self.highscore_path)

            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)

            with open(self.highscore_path, "w") as f:
                json.dump({"best_score": self.best_score}, f)

        except Exception:
            pass

    # =============================
    # DISTANCE
    # =============================

    def distance(self, a, b):

        return math.sqrt(
            (a.x - b.x) ** 2 +
            (a.y - b.y) ** 2
        )

    # =============================
    # SHOULDER WIDTH (SCALE REFERENCE)
    # =============================

    def get_shoulder_width(self, landmarks):

        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]

        width = self.distance(left_shoulder, right_shoulder)

        # Guard against a degenerate/near-zero reading
        if width < 0.02:
            return 0.20

        return width

    # =============================
    # GUARD DETECTION
    # =============================

    def detect_guard_raw(self, landmarks):

        left = landmarks[15]
        right = landmarks[16]
        nose = landmarks[0]

        shoulder_width = self.get_shoulder_width(landmarks)

        # Threshold scales with the player's body size instead of a
        # fixed normalized number, so it holds up at different camera
        # distances.
        threshold = shoulder_width * 1.15

        return (
            self.distance(left, nose) < threshold
            and
            self.distance(right, nose) < threshold
        )

    def detect_guard(self, landmarks):

        raw = self.detect_guard_raw(landmarks)

        self.guard_history.append(raw)

        if len(self.guard_history) > self.guard_history_len:
            self.guard_history.pop(0)

        if len(self.guard_history) < self.guard_history_len:
            return False

        true_ratio = sum(self.guard_history) / len(self.guard_history)

        return true_ratio >= self.guard_confirm_ratio

    # =============================
    # START INTRO
    # =============================

    def start_intro(self):

        self.state = "INTRO"

        self.intro_start = time.time()

        self.score = 0
        self.combo = 0
        self.max_combo = 0

        self.total_punches = 0
        self.total_hits = 0

        self.punch_type_counts = {
            "JAB": 0,
            "CROSS": 0,
            "HOOK": 0,
            "UPPERCUT": 0,
        }

    # =============================
    # INTRO
    # =============================

    def update_intro(self):

        if time.time() - self.intro_start >= self.intro_duration:

            self.state = "COUNTDOWN"

            self.countdown_start = time.time()

            self.countdown_value = 3

    # =============================
    # COUNTDOWN
    # =============================

    def update_countdown(self):

        elapsed = time.time() - self.countdown_start

        if elapsed >= 3:

            self.state = "FIGHT"

            self.round_start = time.time()

            self.spawn_target()

        else:

            self.countdown_value = 3 - int(elapsed)

    # =============================
    # TIMER
    # =============================

    def get_time_left(self):

        if self.round_start is None:
            return self.round_duration

        elapsed = time.time() - self.round_start

        # Difficulty ramps from 0 -> 1 over the course of the round
        self.difficulty = min(elapsed / self.round_duration, 1.0)

        remaining = self.round_duration - int(elapsed)

        if remaining <= 0:
            self.end_game()
            return 0

        return remaining

    # =============================
    # END GAME
    # =============================

    def end_game(self):

        self.state = "FINISHED"

        self.final_score = self.score

        if self.score > self.best_score:
            self.best_score = self.score
            self.save_highscore()

    # =============================
    # TARGET
    # =============================

    def spawn_target(self):

        # As difficulty increases, targets get smaller and appear more
        # briefly, and bonus/decoy targets become more likely.
        radius = self.base_target_radius - (
            (self.base_target_radius - self.min_target_radius) * self.difficulty
        )

        roll = random.random()

        if roll < 0.15 + (0.10 * self.difficulty):
            target_type = "BONUS"
            radius *= 0.7
        elif roll < 0.25 + (0.10 * self.difficulty):
            target_type = "DECOY"
        else:
            target_type = "NORMAL"

        margin = 150

        self.target = {
            "x": random.randint(margin, self.frame_w - margin),
            "y": random.randint(margin, self.frame_h - margin),
            "type": target_type,
            "radius": radius,
            "spawned_at": time.time(),
        }

    def move_target(self):

        if self.target is None:
            self.spawn_target()
            return

        move_delay = self.base_target_move_delay - (
            (self.base_target_move_delay - self.min_target_move_delay) * self.difficulty
        )

        if time.time() - self.last_target_move > move_delay:
            self.spawn_target()
            self.last_target_move = time.time()

    # =============================
    # PUNCH CLASSIFICATION
    # =============================

    def classify_punch(self, hand, wrist, elbow, shoulder, dx, dy):
        """
        Classifies a punch as JAB / CROSS / HOOK / UPPERCUT based on the
        wrist's movement direction relative to the shoulder-elbow-wrist
        arm geometry, rather than raw speed alone.

        - UPPERCUT: strong upward (negative y) movement
        - HOOK: strong lateral (sideways) movement relative to forward
                extension, arm bent
        - JAB / CROSS: primarily forward (toward camera / straight out)
                movement with the arm extending. LEFT hand = JAB,
                RIGHT hand = CROSS, matching orthodox stance convention.
        """

        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Arm extension: distance from shoulder to wrist growing means
        # a straight-ish punch (jab/cross); a bent arm with big lateral
        # travel means a hook.
        shoulder_to_wrist = self.distance(wrist, shoulder)
        shoulder_to_elbow = self.distance(elbow, shoulder)
        elbow_to_wrist = self.distance(wrist, elbow)

        arm_extension_ratio = shoulder_to_wrist / max(
            shoulder_to_elbow + elbow_to_wrist, 0.01
        )

        # Strong upward motion -> uppercut
        if dy < -0.02 and abs_dy > abs_dx * 1.2:
            return "UPPERCUT"

        # Mostly straight arm with forward/vertical dominant motion -> jab/cross
        if arm_extension_ratio > 0.85 and abs_dy >= abs_dx * 0.6:
            return "JAB" if hand == "LEFT" else "CROSS"

        # Otherwise, lateral dominant motion with bent arm -> hook
        if abs_dx > abs_dy:
            return "HOOK"

        return "JAB" if hand == "LEFT" else "CROSS"

    # =============================
    # ADVANCED PUNCH DETECTION (PER HAND)
    # =============================

    def detect_punches(self, landmarks):
        """
        Returns a list of punch dicts (0, 1, or 2 entries) detected this
        frame — one independent check per hand, so simultaneous punches
        from both hands are never lost.
        """

        now = time.time()

        shoulder_width = self.get_shoulder_width(landmarks)

        wrists = {
            "LEFT": landmarks[15],
            "RIGHT": landmarks[16],
        }

        elbows = {
            "LEFT": landmarks[13],
            "RIGHT": landmarks[14],
        }

        shoulders = {
            "LEFT": landmarks[11],
            "RIGHT": landmarks[12],
        }

        punches = []

        for hand in ("LEFT", "RIGHT"):

            state = self.hand_state[hand]

            wrist = wrists[hand]
            elbow = elbows[hand]
            shoulder = shoulders[hand]

            if state["last_wrist"] is not None and (now - state["last_punch_time"]) >= self.punch_cooldown:

                dx = wrist.x - state["last_wrist"].x
                dy = wrist.y - state["last_wrist"].y

                raw_distance = math.sqrt(dx * dx + dy * dy)

                dt = max(now - state["last_sample_time"], self.min_dt)

                # Velocity = distance / time, then normalized against
                # shoulder width. Units: shoulder-widths per second.
                # This is frame-rate independent (unlike raw per-frame
                # distance) and camera-distance independent (thanks to
                # the shoulder-width normalization).
                velocity = raw_distance / dt

                speed_ratio = velocity / shoulder_width

                self.last_measured_speed = round(speed_ratio, 2)

                if speed_ratio > self.min_punch_speed_ratio:

                    punch_type = self.classify_punch(
                        hand, wrist, elbow, shoulder, dx, dy
                    )

                    # Power scales with velocity, capped at 100.
                    power = min(int(speed_ratio * 6), 100)

                    punches.append({
                        "hand": hand,
                        "wrist": wrist,
                        "type": punch_type,
                        "speed": round(speed_ratio, 2),
                        "power": power,
                    })

                    state["last_punch_time"] = now

            state["last_wrist"] = wrist
            state["last_elbow"] = elbow
            state["last_shoulder"] = shoulder
            state["last_sample_time"] = now

        return punches

    # =============================
    # HIT CHECK
    # =============================

    def check_hit(self, punch):

        self.total_punches += 1

        if self.punch_type_counts.get(punch["type"]) is not None:
            self.punch_type_counts[punch["type"]] += 1

        self.last_punch_info = punch

        if self.target is None:
            self.combo = 0
            return False

        wrist = punch["wrist"]
        power = punch["power"]
        hand = punch["hand"]

        x = wrist.x * self.frame_w
        y = wrist.y * self.frame_h

        dist = math.sqrt(
            (x - self.target["x"]) ** 2 +
            (y - self.target["y"]) ** 2
        )

        target_type = self.target["type"]
        radius = self.target["radius"]

        if dist < radius:

            self.last_hit_was_bonus = (target_type == "BONUS")
            self.last_hit_was_decoy = (target_type == "DECOY")

            if target_type == "DECOY":
                # Hitting a decoy breaks the combo and scores nothing.
                self.combo = 0
                self.spawn_target()
                return False

            base_points = 10 + int(power / 10)

            if target_type == "BONUS":
                base_points = int(base_points * 2.5)

            self.score += base_points

            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)

            self.total_hits += 1

            self.hit = True
            self.hit_time = time.time()

            self.spawn_target()

            return True

        else:

            self.combo = 0
            self.last_hit_was_bonus = False
            self.last_hit_was_decoy = False

        return False

    # =============================
    # UPDATE
    # =============================

    def update(self, pose_results):

        if self.state == "FINISHED":
            return

        if pose_results is None:
            return

        if not pose_results.pose_landmarks:
            return

        landmarks = pose_results.pose_landmarks[0]

        if self.state == "WAITING":

            if self.detect_guard(landmarks):
                self.start_intro()

        elif self.state == "INTRO":

            self.update_intro()

        elif self.state == "COUNTDOWN":

            self.update_countdown()

        elif self.state == "FIGHT":

            if self.get_time_left() == 0:
                return

            self.move_target()

            punches = self.detect_punches(landmarks)

            for punch in punches:
                self.check_hit(punch)

    # =============================
    # RESET
    # =============================

    def reset(self):

        self.state = "WAITING"

        self.intro_start = None
        self.countdown_start = None
        self.round_start = None

        self.score = 0
        self.combo = 0
        self.max_combo = 0

        self.total_punches = 0
        self.total_hits = 0

        self.punch_type_counts = {
            "JAB": 0,
            "CROSS": 0,
            "HOOK": 0,
            "UPPERCUT": 0,
        }

        self.target = None

        self.guard_history = []

        self.difficulty = 0.0

        for hand in self.hand_state:
            self.hand_state[hand] = {
                "last_wrist": None,
                "last_elbow": None,
                "last_shoulder": None,
                "last_sample_time": 0,
                "last_punch_time": 0,
                "extending": False,
                "start_wrist": None,
                "start_time": 0,
            }

    # =============================
    # ACCURACY
    # =============================

    def get_accuracy(self):

        if self.total_punches == 0:
            return 0

        return int((self.total_hits / self.total_punches) * 100)

    # =============================
    # STATUS
    # =============================

    def get_status(self):

        return {

            "state": self.state,

            "countdown": self.countdown_value,

            "score": self.score,

            "combo": self.combo,

            "max_combo": self.max_combo,

            "target": self.target,

            "hit": self.hit,

            "time": self.get_time_left(),

            "final_score": self.final_score,

            "best_score": self.best_score,

            "accuracy": self.get_accuracy(),

            "total_punches": self.total_punches,

            "total_hits": self.total_hits,

            "punch_types": self.punch_type_counts,

            "last_punch": self.last_punch_info,

            "difficulty": self.difficulty,

            "last_hit_was_bonus": self.last_hit_was_bonus,

            "last_hit_was_decoy": self.last_hit_was_decoy,

            "last_measured_speed": self.last_measured_speed,

            "punch_threshold": self.min_punch_speed_ratio,
        }