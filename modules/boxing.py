"""
modules/boxing.py
---------------------------------
AI Gesture Experience

Advanced AI Boxing Engine

Features:
- Guard detection
- Intro
- Countdown
- 60 second fight
- Moving target
- Punch velocity
- Accuracy scoring
- Combo system
- Game over
- Retry system

Author: Shane
"""

import math
import time
import random


class BoxingEngine:


    best_score_global = 0


    def __init__(self):


        self.state = "WAITING"


        self.intro_time = None
        self.countdown_time = None
        self.start_time = None


        self.round_time = 60


        self.score = 0
        self.combo = 0
        self.final_score = 0



        # punch

        self.last_left_wrist = None
        self.last_right_wrist = None

        self.last_punch_time = 0
        self.punch_cooldown = 0.35



        # target

        self.target = None

        self.target_speed = 3

        self.target_direction = [
            random.choice([-1,1]),
            random.choice([-1,1])
        ]



        # feedback

        self.last_hit = ""

        self.last_hit_time = 0



    # =============================
    # DISTANCE
    # =============================

    def distance(self,a,b):

        return math.sqrt(
            (a.x-b.x)**2+
            (a.y-b.y)**2
        )



    # =============================
    # GUARD
    # =============================

    def detect_guard(self,landmarks):

        nose = landmarks[0]

        left = landmarks[15]
        right = landmarks[16]


        return (
            self.distance(left,nose)<0.35
            and
            self.distance(right,nose)<0.35
        )



    # =============================
    # START
    # =============================

    def start_game(self):

        self.state="INTRO"

        self.intro_time=time.time()

        self.score=0
        self.combo=0



    # =============================
    # INTRO
    # =============================

    def update_intro(self):

        if time.time()-self.intro_time >=14:

            self.state="COUNTDOWN"

            self.countdown_time=time.time()



    # =============================
    # COUNTDOWN
    # =============================

    def update_countdown(self):

        value = 3-int(
            time.time()-self.countdown_time
        )


        if value<=0:

            self.state="PLAYING"

            self.start_time=time.time()

            self.spawn_target()


        return max(value,0)



    # =============================
    # TIMER
    # =============================

    def time_left(self):

        if self.start_time is None:
            return 60


        remaining = (
            self.round_time -
            int(time.time()-self.start_time)
        )


        if remaining<=0:

            self.end_game()

            return 0


        return remaining



    # =============================
    # END
    # =============================

    def end_game(self):

        if self.state=="FINISHED":
            return


        self.state="FINISHED"


        self.final_score=self.score


        if self.score > BoxingEngine.best_score_global:

            BoxingEngine.best_score_global=self.score




    # =============================
    # RESET
    # =============================

    def retry(self):

        self.state="WAITING"

        self.score=0

        self.combo=0

        self.target=None

        self.start_time=None

        self.last_left_wrist=None
        self.last_right_wrist=None

        self.last_hit=""



    # =============================
    # TARGET
    # =============================

    def spawn_target(self):

        self.target={

            "x":random.randint(
                200,
                1050
            ),

            "y":random.randint(
                150,
                550
            )

        }



    def move_target(self):

        if not self.target:
            return


        speed = (
            self.target_speed
            +
            self.combo*0.3
        )


        self.target["x"] += (
            self.target_direction[0]
            *
            speed
        )

        self.target["y"] += (
            self.target_direction[1]
            *
            speed
        )



        if self.target["x"]<100 or self.target["x"]>1180:

            self.target_direction[0]*=-1


        if self.target["y"]<100 or self.target["y"]>650:

            self.target_direction[1]*=-1



    # =============================
    # PUNCH
    # =============================

    def detect_punch(self,landmarks):

        now=time.time()


        if now-self.last_punch_time < self.punch_cooldown:

            return None



        left=landmarks[15]
        right=landmarks[16]


        punch=None


        if self.last_left_wrist:

            speed=self.distance(
                left,
                self.last_left_wrist
            )


            if speed>0.10:

                punch=left



        if self.last_right_wrist:

            speed=self.distance(
                right,
                self.last_right_wrist
            )


            if speed>0.10:

                punch=right



        self.last_left_wrist=left
        self.last_right_wrist=right



        if punch:

            self.last_punch_time=now

            return punch


        return None



    # =============================
    # HIT
    # =============================

    def check_hit(self,wrist):


        if not self.target:
            return False



        x=wrist.x*1280
        y=wrist.y*720



        d=math.sqrt(
            (x-self.target["x"])**2+
            (y-self.target["y"])**2
        )



        if d<30:

            points=50
            text="PERFECT +50"


        elif d<60:

            points=25
            text="GREAT +25"


        elif d<90:

            points=10
            text="HIT +10"


        else:

            self.combo=0
            return False



        self.score+=points

        self.combo+=1


        self.last_hit=text

        self.last_hit_time=time.time()


        self.spawn_target()


        return True



    # =============================
    # UPDATE
    # =============================

    def update(self,pose_results):


        if pose_results is None:
            return


        if not pose_results.pose_landmarks:
            return



        landmarks=pose_results.pose_landmarks[0]



        if self.state=="WAITING":

            if self.detect_guard(landmarks):

                self.start_game()



        elif self.state=="INTRO":

            self.update_intro()



        elif self.state=="COUNTDOWN":

            self.update_countdown()



        elif self.state=="PLAYING":


            if self.time_left()==0:

                return



            self.move_target()


            punch=self.detect_punch(
                landmarks
            )


            if punch:

                self.check_hit(
                    punch
                )



    # =============================
    # STATUS
    # =============================

    def get_status(self):


        return {

            "state":self.state,

            "score":self.score,

            "combo":self.combo,

            "target":self.target,

            "time":self.time_left(),

            "countdown":
                self.update_countdown()
                if self.state=="COUNTDOWN"
                else 0,

            "hit":self.last_hit,

            "final_score":self.final_score,

            "best_score":
                BoxingEngine.best_score_global
        }