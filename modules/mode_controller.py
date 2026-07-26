"""
modules/mode_controller.py
---------------------------------
AI Gesture Experience

Application Mode Controller

Handles:
- Main modes
- Entertainment games
- Switching systems

Author: Shane
"""

import cv2



class ModeController:


    def __init__(self):

        # MAIN MODE
        self.current_mode = None


        # ENTERTAINMENT GAME
        self.current_game = "BOXING"



    # =============================
    # SET MAIN MODE
    # =============================

    def set_mode(self, mode):

        self.current_mode = mode



    # =============================
    # SET ENTERTAINMENT GAME
    # =============================

    def set_game(self, game):

        self.current_game = game




    # =============================
    # GET GAME
    # =============================

    def get_game(self):

        return self.current_game





    # =============================
    # DRAW MODE TITLE
    # =============================

    def draw(self, frame):


        h,w,_ = frame.shape


        if self.current_mode is None:

            return



        # -----------------------------
        # PROFESSIONAL
        # -----------------------------

        if self.current_mode == 0:


            title = "PROFESSIONAL MODE"

            color = (
                255,
                255,
                255
            )




        # -----------------------------
        # ENTERTAINMENT
        # -----------------------------

        elif self.current_mode == 1:


            title = (
                "ENTERTAINMENT : "
                +
                self.current_game
            )


            color = (
                0,
                0,
                255
            )




        # -----------------------------
        # AR
        # -----------------------------

        elif self.current_mode == 2:


            title = "AR EXPERIENCE"

            color = (
                255,
                0,
                255
            )



        else:

            return





        cv2.putText(

            frame,

            title,

            (
                w//2-300,
                80
            ),

            cv2.FONT_HERSHEY_DUPLEX,

            1.5,

            color,

            3,

            cv2.LINE_AA

        )