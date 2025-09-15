"""
Custom title bar utilities for Windows
"""
import ctypes
from ctypes import wintypes

# Windows API constants
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19

# Load required DLLs
user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

def set_title_bar_color(hwnd, is_dark):
    """
    Set title bar color for Windows 11
    """
    try:
        # Try Windows 11 dark mode
        value = ctypes.c_int(1 if is_dark else 0)
        dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )
    except:
        try:
            # Try Windows 10 dark mode
            dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
        except:
            pass  # Not supported on this Windows version

def get_hwnd_from_widget(widget):
    """
    Get Windows HWND from Qt widget
    """
    try:
        return int(widget.winId())
    except:
        return None