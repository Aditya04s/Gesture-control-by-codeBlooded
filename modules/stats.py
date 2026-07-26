"""
stats.py
------------------------------------------
AI Gesture Experience

Statistics & Leaderboard Manager

Author: Shane
"""

import json
import os
from datetime import datetime


class StatsManager:

    def __init__(self):

        self.file = "data/stats.json"

        self.data = {
            "launches": 0,
            "gestures_detected": 0,
            "mouse_clicks": 0,
            "screenshots": 0,
            "visitor_sessions": 0,
            "highest_score": 0,
            "last_opened": ""
        }

        self.load()

    def load(self):

        if os.path.exists(self.file):

            try:

                with open(self.file, "r") as f:

                    self.data = json.load(f)

            except:

                self.save()

    def save(self):

        os.makedirs("data", exist_ok=True)

        with open(self.file, "w") as f:

            json.dump(
                self.data,
                f,
                indent=4
            )

    def app_started(self):

        self.data["launches"] += 1
        self.data["last_opened"] = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        self.save()

    def gesture_detected(self):

        self.data["gestures_detected"] += 1

    def mouse_clicked(self):

        self.data["mouse_clicks"] += 1

    def screenshot_taken(self):

        self.data["screenshots"] += 1

    def visitor_started(self):

        self.data["visitor_sessions"] += 1

    def update_score(self, score):

        if score > self.data["highest_score"]:

            self.data["highest_score"] = score

            self.save()

    def get(self):

        return self.data