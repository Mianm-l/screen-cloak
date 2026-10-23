"""
Privacy Mask Window implementation with native click-through support.
"""

import tkinter as tk
import ctypes
from typing import Optional, Callable

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
SWP_FLAGS = 0x0020 | 0x0002 | 0x0001 | 0x0004  # FRAMECHANGED | NOMOVE | NOSIZE | NOZORDER

user32 = ctypes.windll.user32

class PrivacyMask:
    def __init__(
        self,
        master: tk.Tk,
        mask_id: int,
        x: int = 200,
        y: int = 200,
        width: int = 360,
        height: int = 70,
        label: str = "CONFIDENTIAL",
        style: str = "redacted",
        on_close: Optional[Callable[["PrivacyMask"], None]] = None
    ):
        self.master = master
        self.mask_id = mask_id
        self.label_text = label
        self.style = style
        self.on_close = on_close

        self.is_locked = False  # False: Edit Mode (movable/resizable), True: Locked (Click-through)
        self.is_visible = True

        # Window Tracking / Anchoring
        self.target_hwnd: Optional[int] = None
        self.anchor_offset: Optional[tuple] = None  # (rel_x, rel_y, rel_w, rel_h)

        # Create TopLevel window
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.geometry(f"{width}x{height}+{x}+{y}")

        # Drag & Resize state
        self._drag_data = {"x": 0, "y": 0}
        self._resize_data = {"x": 0, "y": 0, "w": width, "h": height}

        # Build UI
        self._build_ui()
        self.win.update_idletasks()

        # Cache native HWND
        self.hwnd = user32.GetParent(self.win.winfo_id())
        if not self.hwnd:
            self.hwnd = self.win.winfo_id()

    def _build_ui(self):
        # Master Canvas for drawing border, background, and badge
        self.canvas = tk.Canvas(self.win, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events on canvas for moving
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)

        # Controls overlay (Close button, resize handle, mode badge)
        self._render_content()

    def _render_content(self):
        self.canvas.delete("all")
        w = self.win.winfo_width()
        h = self.win.winfo_height()
        if w < 10: w = 360
        if h < 10: h = 70

        if not self.is_locked:
            # === EDIT MODE ===
            # Cyber dark border with dashed active outline
            bg_color = "#18181b"
            border_color = "#3b82f6"  # Blue accent
            self.canvas.configure(bg=bg_color)

            # Draw outer rectangle border
            self.canvas.create_rectangle(
                1, 1, w - 2, h - 2,
                outline=border_color, width=2, dash=(6, 4)
            )

            # Header Badge
            badge_text = f"🛡️ 防窥条 #{self.mask_id} [{self.label_text}]"
            self.canvas.create_text(
                10, 16, text=badge_text,
                anchor="w", fill="#93c5fd",
                font=("Consolas", 10, "bold")
            )

            # Center Hint
            self.canvas.create_text(
                w // 2, h // 2 + 5,
                text="[ 拖动移动 | 右下角调整大小 | 按 Ctrl+Alt+C 锁定穿透 ]",
                fill="#64748b", font=("Segoe UI", 9)
            )

            # Close button (top right)
            self.close_btn_id = self.canvas.create_text(
                w - 15, 15, text="✕",
                fill="#ef4444", font=("Segoe UI", 11, "bold")
            )
            self.canvas.tag_bind(self.close_btn_id, "<Button-1>", self._on_close_clicked)

            # Resize grip (bottom right)
            self.grip_id = self.canvas.create_text(
                w - 10, h - 10, text="⤡",
                fill="#3b82f6", font=("Segoe UI", 12, "bold")
            )
            self.canvas.tag_bind(self.grip_id, "<Button-1>", self._on_resize_start)
            self.canvas.tag_bind(self.grip_id, "<B1-Motion>", self._on_resize_motion)

        else:
            # === LOCKED MODE (CENSOR / REDACTED BAR) ===
            if self.style == "warning":
                bg_color = "#0a0a0c"
                border_color = "#eab308"
                text_color = "#fef08a"
                banner_text = f"⚠️ [ CLASSIFIED - {self.label_text.upper()} PROTECTED ] ⚠️"
            elif self.style == "pure_black":
                bg_color = "#000000"
                border_color = "#000000"
                text_color = "#333333"
                banner_text = f"[ REDACTED ]"
            else:  # "redacted" (default dark obsidian with gold/cyber accent)
                bg_color = "#09090b"
                border_color = "#27272a"
                text_color = "#d4af37"  # Metallic gold
                banner_text = f"🔒 [ SENSITIVE DATA REDACTED • {self.label_text.upper()} ]"

            self.canvas.configure(bg=bg_color)
            self.canvas.create_rectangle(
                0, 0, w, h,
                fill=bg_color, outline=border_color, width=1
            )

            # Center Banner Text
            self.canvas.create_text(
                w // 2, h // 2,
                text=banner_text,
                fill=text_color,
                font=("Consolas", 10, "bold")
            )

    def set_locked(self, locked: bool):
        """
        Switches between Edit Mode (interactive) and Locked Mode (click-through).
        """
        self.is_locked = locked
        self._render_content()

        if not self.hwnd:
            return

        ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        if locked:
            # Enable WS_EX_TRANSPARENT -> Click-through enabled!
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        else:
            # Disable WS_EX_TRANSPARENT -> Edit handles enabled!
            user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex_style & ~WS_EX_TRANSPARENT)

        user32.SetWindowPos(self.hwnd, 0, 0, 0, 0, 0, SWP_FLAGS)

    def set_style(self, style_name: str):
        self.style = style_name
        self._render_content()

    def set_visible(self, visible: bool):
        self.is_visible = visible
        if visible:
            self.win.deiconify()
        else:
            self.win.withdraw()

    def get_geometry(self):
        return {
            "x": self.win.winfo_x(),
            "y": self.win.winfo_y(),
            "w": self.win.winfo_width(),
            "h": self.win.winfo_height(),
            "label": self.label_text,
            "style": self.style
        }

    # Drag Handlers
    def _on_drag_start(self, event):
        if self.is_locked:
            return
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        if self.is_locked:
            return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        new_x = self.win.winfo_x() + dx
        new_y = self.win.winfo_y() + dy
        self.win.geometry(f"+{new_x}+{new_y}")

    # Resize Handlers
    def _on_resize_start(self, event):
        if self.is_locked:
            return
        self._resize_data["x"] = event.x_root
        self._resize_data["y"] = event.y_root
        self._resize_data["w"] = self.win.winfo_width()
        self._resize_data["h"] = self.win.winfo_height()

    def _on_resize_motion(self, event):
        if self.is_locked:
            return
        dw = event.x_root - self._resize_data["x"]
        dh = event.y_root - self._resize_data["y"]
        new_w = max(180, self._resize_data["w"] + dw)
        new_h = max(40, self._resize_data["h"] + dh)
        self.win.geometry(f"{new_w}x{new_h}")
        self._render_content()

    def _on_close_clicked(self, event):
        self.destroy()
        if self.on_close:
            self.on_close(self)

    def destroy(self):
        try:
            self.win.destroy()
        except Exception:
            pass
