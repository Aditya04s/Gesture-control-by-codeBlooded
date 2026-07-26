"""
modules/audio.py
---------------------------------
AI Gesture Experience

Audio Manager

Handles:
- Background music
- Sound effects
- Game audio

Author: Shane
"""

import pygame
import os



class AudioManager:


    def __init__(self):

        pygame.mixer.init()

        self.sound_folder = "assets/sounds"

        self.sounds = {}

        self.load_sounds()



    # ---------------------------------
    # LOAD SOUND EFFECTS
    # ---------------------------------

    def load_sounds(self):


        files = {


            # Existing sounds

            "click":
            "click.wav",


            "success":
            "success.wav",


            "error":
            "error.wav",



            # Boxing sounds

            "countdown":
            "countdown.wav",


            "bell":
            "bell.wav",


            "punch":
            "punch.wav",


            # AI Coach / exhibition sounds
            # NOTE: these files are optional — load_sounds() already
            # skips any file that doesn't exist on disk, so nothing
            # breaks if you haven't added these .wav files yet. Add
            # them to assets/sounds/ whenever you want the coach to
            # have actual voice/reaction audio instead of silent cues.

            "combo":
            "combo.wav",


            "bonus":
            "bonus.wav",


            "decoy":
            "decoy.wav",


            "round_end":
            "round_end.wav",


            "new_highscore":
            "new_highscore.wav"

        }



        for name, file in files.items():


            path = os.path.join(
                self.sound_folder,
                file
            )


            if os.path.exists(path):


                self.sounds[name] = (
                    pygame.mixer.Sound(path)
                )



    # ---------------------------------
    # PLAY SOUND EFFECT
    # ---------------------------------

    def play_sound(self, name):


        if name in self.sounds:

            self.sounds[name].play()



    # ---------------------------------
    # OLD COMPATIBILITY
    # ---------------------------------

    def play(self, name):

        self.play_sound(name)




    # ---------------------------------
    # PLAY MUSIC
    # ---------------------------------

    def play_music(self, file):


        path = os.path.join(
            self.sound_folder,
            file
        )


        if os.path.exists(path):


            pygame.mixer.music.load(
                path
            )


            # Play once
            pygame.mixer.music.play()



    # ---------------------------------
    # STOP MUSIC
    # ---------------------------------

    def stop_music(self):

        pygame.mixer.music.stop()



    # ---------------------------------
    # STOP EVERYTHING
    # ---------------------------------

    def stop_all(self):

        pygame.mixer.stop()

        pygame.mixer.music.stop()