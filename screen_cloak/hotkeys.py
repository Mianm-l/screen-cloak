"""
Global hotkey manager using Win32 RegisterHotKey and background message loop.
"""

import ctypes
import ctypes.wintypes
import threading
from typing import Dict, Callable, Optional

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

WM_HOTKEY = 0x0312

class GlobalHotkeyManager:
    def __init__(self):
        self._hotkeys: Dict[int, Callable[[], None]] = {}
        self._next_id = 1
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def register(self, modifiers: int, vk_code: int, callback: Callable[[], None]) -> int:
        hotkey_id = self._next_id
        self._next_id += 1
        self._hotkeys[hotkey_id] = (modifiers, vk_code, callback)
        return hotkey_id

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        # Register in this thread's message queue
        registered_ids = []
        for hk_id, (mods, vk, cb) in self._hotkeys.items():
            if user32.RegisterHotKey(None, hk_id, mods | MOD_NOREPEAT, vk):
                registered_ids.append(hk_id)

        msg = ctypes.wintypes.MSG()
        while self._running:
            # PeekMessage or GetMessage
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break
            if msg.message == WM_HOTKEY:
                hk_id = msg.wParam
                if hk_id in self._hotkeys:
                    _, _, cb = self._hotkeys[hk_id]
                    try:
                        cb()
                    except Exception as e:
                        print(f"[!] Hotkey callback error: {e}")

        # Cleanup
        for hk_id in registered_ids:
            user32.UnregisterHotKey(None, hk_id)

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            # Post a quit message to break GetMessage
            user32.PostQuitMessage(0)
