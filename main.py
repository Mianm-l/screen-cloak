"""
ScreenCloak entry point.
Run with: python main.py
"""

import sys
from screen_cloak.app import ScreenCloakApp

def main():
    app = ScreenCloakApp()
    app.run()

if __name__ == "__main__":
    main()
