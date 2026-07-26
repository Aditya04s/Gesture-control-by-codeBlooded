"""
modules/window_lock.py
---------------------------------
Hooks into the native Win32 window procedure of an OpenCV HighGUI window
to enforce a fixed aspect ratio while the user drags to resize it —
this is what actually constrains the drag itself (Canva-style),
as opposed to letterboxing which only fixes content after the fact.
"""

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

WM_SIZING = 0x0214
WMSZ_LEFT = 1
WMSZ_RIGHT = 2
WMSZ_TOP = 3
WMSZ_TOPLEFT = 4
WMSZ_TOPRIGHT = 5
WMSZ_BOTTOM = 6
WMSZ_BOTTOMLEFT = 7
WMSZ_BOTTOMRIGHT = 8

GWLP_WNDPROC = -4


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)

user32.CallWindowProcW.restype = LRESULT
user32.CallWindowProcW.argtypes = [
    ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
]

# 64-bit vs 32-bit Windows use different function names for this API
if ctypes.sizeof(ctypes.c_void_p) == 8:
    _SetWindowLongPtr = user32.SetWindowLongPtrW
    _GetWindowLongPtr = user32.GetWindowLongPtrW
else:
    _SetWindowLongPtr = user32.SetWindowLongW
    _GetWindowLongPtr = user32.GetWindowLongW

_SetWindowLongPtr.restype = ctypes.c_void_p
_SetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
_GetWindowLongPtr.restype = ctypes.c_void_p
_GetWindowLongPtr.argtypes = [wintypes.HWND, ctypes.c_int]


class AspectRatioLock:
    """
    Locks a named OpenCV window to a fixed aspect ratio during resize.
    Whichever edge/corner the user drags, the opposite dimension is
    recalculated live so width:height never changes.
    """

    def __init__(self, window_title, aspect_w, aspect_h):
        self.aspect_ratio = aspect_w / aspect_h

        self.hwnd = user32.FindWindowW(None, window_title)
        if not self.hwnd:
            raise RuntimeError(
                f"Could not find native window handle for '{window_title}'. "
                "Call cv2.imshow() at least once (so the OS window actually "
                "exists) before creating AspectRatioLock."
            )

        # Keep a reference to the callback — if it gets garbage collected,
        # Windows will call into freed memory and crash the process.
        self._new_proc = WNDPROC(self._wnd_proc)
        self._old_proc = _GetWindowLongPtr(self.hwnd, GWLP_WNDPROC)
        _SetWindowLongPtr(
            self.hwnd, GWLP_WNDPROC, ctypes.cast(self._new_proc, ctypes.c_void_p)
        )

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_SIZING:
            rect = ctypes.cast(lparam, ctypes.POINTER(RECT)).contents
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            edge = wparam

            if edge in (WMSZ_LEFT, WMSZ_RIGHT):
                # user dragged a side handle -> height follows width
                rect.bottom = rect.top + int(width / self.aspect_ratio)
            elif edge in (WMSZ_TOP, WMSZ_BOTTOM):
                # user dragged top/bottom handle -> width follows height
                rect.right = rect.left + int(height * self.aspect_ratio)
            else:
                # corner drag -> width drives, height follows
                new_height = int(width / self.aspect_ratio)
                if edge in (WMSZ_TOPLEFT, WMSZ_TOPRIGHT):
                    rect.top = rect.bottom - new_height
                else:
                    rect.bottom = rect.top + new_height

            return 1  # tell Windows we've already updated the rect

        return user32.CallWindowProcW(self._old_proc, hwnd, msg, wparam, lparam)

    def unhook(self):
        """Restore the original window procedure (call before app exit)."""
        if self._old_proc:
            _SetWindowLongPtr(self.hwnd, GWLP_WNDPROC, self._old_proc)
            self._old_proc = None