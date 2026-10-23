"""
ScreenCloak entry point.
Run with: python main.py
"""

import sys
import os

# Auto-hide console window on Windows if launched via python.exe
if sys.platform == "win32":
    try:
        import ctypes
        console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if console_hwnd:
            # 0 = SW_HIDE
            ctypes.windll.user32.ShowWindow(console_hwnd, 0)
    except Exception:
        pass

from screen_cloak.app import ScreenCloakApp

def main():
    app = ScreenCloakApp()
    app.run()

if __name__ == "__main__":
    main()
