"""
modules/menu.py
---------------------------------
AI Gesture Experience

Main Mode Selection Menu

Author: Shane
"""

import cv2
import time



class ModeMenu:


    def __init__(self):


        self.selected_time = 0

        self.required_time = 1.5

        self.last_count = 0





    # =============================
    # DRAW MENU
    # =============================

    def draw(self, frame, finger_count):


        h,w,_ = frame.shape



        # background

        frame[:] = (
            45,
            45,
            45
        )




        cv2.putText(

            frame,

            "AI GESTURE EXPERIENCE",

            (
                w//2-300,
                100
            ),

            cv2.FONT_HERSHEY_DUPLEX,

            1.5,

            (
                255,
                255,
                255
            ),

            3

        )





        cv2.putText(

            frame,

            "Show Fingers To Select Mode",

            (
                w//2-250,
                160
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            1,

            (
                180,
                180,
                180
            ),

            2

        )





        modes=[


            "1  PROFESSIONAL MODE",


            "2  ENTERTAINMENT MODE",


         


        ]



        y=280



        for i,text in enumerate(modes):


            color=(200,200,200)



            if finger_count == i+1:


                color=(0,255,0)



                cv2.circle(

                    frame,

                    (
                        w//2-300,
                        y-10
                    ),

                    15,

                    (
                        0,
                        255,
                        0
                    ),

                    -1

                )




            cv2.putText(

                frame,

                text,

                (
                    w//2-250,
                    y
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                color,

                3

            )


            y += 80





        # =============================
        # SELECTION TIMER
        # =============================


        if finger_count in [1,2]:


            if self.last_count != finger_count:


                self.selected_time=time.time()

                self.last_count=finger_count





            remaining = (

                self.required_time -

                (
                    time.time()
                    -
                    self.selected_time
                )

            )



            cv2.putText(

                frame,

                f"HOLD {remaining:.1f}",

                (
                    w//2-80,
                    500
                ),

                cv2.FONT_HERSHEY_DUPLEX,

                1.5,

                (
                    0,
                    255,
                    255
                ),

                3

            )





            if (
                time.time()
                -
                self.selected_time
                >
                self.required_time
            ):


                self.last_count=0


                return finger_count-1





        else:


            self.last_count=0




        return None