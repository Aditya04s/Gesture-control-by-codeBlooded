"""
modules/smart_context.py
---------------------------------
Context-Aware OS Interceptor
"""

import threading
import time
import ctypes
import pyautogui

class SmartContextManager:
    def __init__(self):
        self.current_profile = "NORMAL"
        self.running = True
        
        # Action State Variables
        self.is_active = False
        self.baseline_x = None
        self.baseline_y = None
        self.dead_zone = 0.05  # Movement required before triggering an action
        # Start background window monitor (Runs independently of the camera)
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        self.last_action_time = 0
        self.action_cooldown = 0.6

    def _get_active_window_title(self):
        """Uses native Windows API to get the foreground window title safely."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value.lower()
        except:
            return ""

    def _monitor_loop(self):
        """Polls the active window twice a second."""
        while self.running:
            title = self._get_active_window_title()
            
            # Broadened Media Keywords (Streaming, Local Video, Music)
            media_keywords = [
                "youtube", "vlc", "media player", "movies & tv", "films & tv", 
                "spotify", "netflix", "prime video", "twitch", "hulu", "disney+", 
                "itunes", "potplayer", "kmplayer", "mpc-hc", "music", "video"
            ]
            
            # Broadened Document Keywords (PDFs, MS Office, eBooks)
            doc_keywords = [
                ".pdf", "acrobat", "sumatra", "foxit", "reader", "xodo",
                "word", "excel", "powerpoint", "document", "kindle", "calibre"
            ]
            
            # Check which profile matches the active window
            if any(keyword in title for keyword in media_keywords):
                self.current_profile = "MEDIA"
            elif any(keyword in title for keyword in doc_keywords):
                self.current_profile = "PDF"
            else:
                self.current_profile = "NORMAL"
                
            time.sleep(0.5)

    def intercept(self, gesture_name, hand_landmarks):
        """
        Evaluates if the current profile requires hijacking the gesture.
        Returns True if handled, False if main.py should do normal behavior.
        """
        if not hand_landmarks:
            self._reset_state()
            return False

        # ==========================================
        # PROFILE: YOUTUBE / VLC MEDIA
        # ==========================================
        if self.current_profile == "MEDIA":
            if gesture_name == "SCREENSHOT":
                if time.time() - self.last_action_time >= self.action_cooldown:
                    pyautogui.press('space')
                    self.last_action_time = time.time()
                return True
                
            # Hijack Drag -> Timeline Scrub & Volume
            elif gesture_name == "DRAG":
                self._handle_media_drag(hand_landmarks)
                return True
            
        # ==========================================
        # PROFILE: PDF / DOCUMENT READING
        # ==========================================
        elif self.current_profile == "PDF":
            # Hijack Scroll -> Zoom In/Out
            if gesture_name == "SCROLL":
                self._handle_pdf_zoom(hand_landmarks)
                return True

        # If not a smart profile, or an unrelated gesture, wave it through
        self._reset_state()
        return False

    def _handle_media_drag(self, hand_landmarks):
        """Converts dragging into timeline and volume arrow key presses."""
        current_x = hand_landmarks[8].x
        current_y = hand_landmarks[8].y
        
        if not self.is_active:
            self.is_active = True
            self.baseline_x = current_x
            self.baseline_y = current_y
            return
            
        delta_x = current_x - self.baseline_x
        delta_y = current_y - self.baseline_y
        
        # X-Axis Scrubbing (Left/Right arrows)
        if abs(delta_x) > self.dead_zone:
            if delta_x > 0:
                pyautogui.press('right') # Skip forward
            else:
                pyautogui.press('left')  # Skip backward
            self.baseline_x = current_x  
            
        # Y-Axis Volume (Up/Down arrows)
        if abs(delta_y) > self.dead_zone:
            if delta_y < 0:
                pyautogui.press('up')    # Volume Up
            else:
                pyautogui.press('down')  # Volume Down
            self.baseline_y = current_y

    def _handle_pdf_zoom(self, hand_landmarks):
        """Simulates holding Ctrl while scrolling to zoom documents."""
        # Use stable palm center Y
        palm_y = sum([hand_landmarks[i].y for i in [0, 5, 9, 13, 17]]) / 5
        
        if not self.is_active:
            self.is_active = True
            self.baseline_y = palm_y
            return
            
        delta_y = self.baseline_y - palm_y
        
        if abs(delta_y) > (self.dead_zone / 2): # Slightly more sensitive
            pyautogui.keyDown('ctrl')
            if delta_y > 0:
                pyautogui.scroll(300)  # Zoom In
            else:
                pyautogui.scroll(-300) # Zoom Out
            pyautogui.keyUp('ctrl')
            self.baseline_y = palm_y

    def _reset_state(self):
        self.is_active = False
        self.baseline_x = None
        self.baseline_y = None

