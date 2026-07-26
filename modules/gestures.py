"""
modules/gestures.py
---------------------------------
Distance-Normalized Gesture Recognition Engine
"""

import math
import time

class GestureRecognizer:
    def __init__(self):
        # Ratios based on dynamic palm size to ensure distance robustness
        self.pinch_threshold = 0.50       # INCREASED: Makes it much easier to detect the pinch
        self.thumb_extension_ratio = 0.45 # Min horizontal spread for an extended thumb
        
        # Click & Drag State Machine Variables
        self.click_armed = False
        self.pinch_start_time = None
        self.last_click_time = 0
        self.drag_active = False
        self.require_release = False

    def recognize(self, smoothed_landmarks):
        """
        Analyzes hand landmarks to classify gestures.
        Normalized by dynamic palm width to ensure distance robustness.
        """
        if not smoothed_landmarks:
        # NEW: Safely reset all click/drag states if tracking is lost!
            self.pinch_start_time = None
            self.drag_active = False
            self.require_release = False
            return "NO HAND"

        # 1. CALCULATE PALM SCALE (Index MCP to Pinky MCP)
        # Landmark 5 = Index MCP | Landmark 17 = Pinky MCP
        palm_width = self._get_distance(smoothed_landmarks[5], smoothed_landmarks[17])
        if palm_width < 0.001:
            palm_width = 0.01

        # 2. FINGER EXTENSION LOGIC (Using your reliable vertical check)
        # True if Tip.y is higher up on screen (lower value) than the PIP joint
        index_straight = smoothed_landmarks[8].y < smoothed_landmarks[6].y
        middle_straight = smoothed_landmarks[12].y < smoothed_landmarks[10].y
        ring_straight = smoothed_landmarks[16].y < smoothed_landmarks[14].y
        pinky_straight = smoothed_landmarks[20].y < smoothed_landmarks[18].y

        # 3. THUMB EXTENSION CHECK
        # Measure horizontal (X-axis) distance between thumb tip (4) and index knuckle (5)
        thumb_outward_span = abs(smoothed_landmarks[4].x - smoothed_landmarks[5].x)
        thumb_extended = (thumb_outward_span / palm_width) > self.thumb_extension_ratio

        # 4. MEASURE THUMB TO INDEX TIP DISTANCE (For Pinching)
        thumb_index_dist = self._get_distance(smoothed_landmarks[4], smoothed_landmarks[8])
        normalized_pinch = thumb_index_dist / palm_width

        # =====================================================================
        # GESTURE CLASSIFICATION MATRIX - 4 (Anatomy & Timing Optimized)
        # =====================================================================
        current_time = time.time()

        three_fingers_up = middle_straight and ring_straight and pinky_straight
        is_pinching = normalized_pinch < self.pinch_threshold

        # Leniency Lock: If we already started a pinch, don't abort just because 
        # the middle finger twitched downward due to natural tendon movement!
        is_armed = three_fingers_up or (self.pinch_start_time is not None)

        if is_armed:
            if is_pinching:
                if self.require_release:
                    return "UNKNOWN"

                # Only start the initial click timer if fingers were actually up to begin with
                if self.pinch_start_time is None:
                    if not three_fingers_up:
                        return "UNKNOWN"
                    self.pinch_start_time = current_time
                
                elapsed_pinch = current_time - self.pinch_start_time

                # INCREASED to 0.45s: Gives you more time to click without accidentally dragging
                if elapsed_pinch >= 0.45:
                    self.drag_active = True
                    return "DRAG"
                    
                return "UNKNOWN" 
            else:
                # PINCH RELEASED - Fire the click!
                if self.pinch_start_time is not None:
                    elapsed_pinch = current_time - self.pinch_start_time
                    self.pinch_start_time = None
                    
                    if self.drag_active:
                        self.drag_active = False
                        self.require_release = False
                        return "UNKNOWN" 

                    # WIDENED CLICK WINDOW: 0.01s to 0.45s allows for both fast and slow air taps
                    if 0.01 <= elapsed_pinch < 0.45:
                        self.require_release = True
                        
                        # WIDENED DOUBLE CLICK WINDOW: 0.80s gives you plenty of time for the second tap
                        if current_time - self.last_click_time < 0.80:
                            self.last_click_time = 0 
                            return "DOUBLE_CLICK"
                        else:
                            self.last_click_time = current_time
                            return "PINCH" 
                
                self.require_release = False
                
                # If user dropped their safety fingers entirely, we clear out. Otherwise, stay frozen.
                if not three_fingers_up:
                    pass # Will drop down to the reset block below
                else:
                    return "UNKNOWN"

        # 2. Reset states safely if safety fingers are completely dropped
        self.pinch_start_time = None
        self.drag_active = False
        self.require_release = False

        # B: SCREENSHOT (🤙 Shaka / Call Me Gesture)
        if thumb_extended and pinky_straight and not index_straight and not middle_straight and not ring_straight:
            return "SCREENSHOT"

        # C: SCROLL (Index and Middle fingers up, Ring and Pinky down)
        if index_straight and middle_straight and not ring_straight and not pinky_straight:
            return "SCROLL"

        # D: CURSOR (Standard free navigation mode)
        if index_straight and not middle_straight and not ring_straight and not pinky_straight:
            return "CURSOR"

        return "UNKNOWN"

    def _get_distance(self, pt1, pt2):
        """Calculates standard Euclidean 2D distance (Ignoring unstable Z-axis)."""
        return math.sqrt((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)