"""
Privacy Mask Window implementation with native click-through support and smooth resizing.
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

        self.is_locked = False
        self.is_visible = True
        self.is_peeking = False
        self.base_alpha = 1.0

        # Create TopLevel window
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-alpha", self.base_alpha)
        self.win.geometry(f"{width}x{height}+{x}+{y}")

        # Drag & Resize tracking
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
        # Master Canvas for graphics
        self.canvas = tk.Canvas(self.win, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Canvas items
        self.bg_rect_id = self.canvas.create_rectangle(0, 0, 0, 0, width=2)
        self.header_text_id = self.canvas.create_text(10, 16, anchor="w", font=("Consolas", 10, "bold"))
        self.center_text_id = self.canvas.create_text(0, 0, anchor="center", font=("Consolas", 10, "bold"))

        # Bind mouse drag on canvas for moving window
        self.canvas.bind("<Button-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)

        # Dedicated Close Button Widget (Top-Right)
        self.close_btn = tk.Label(
            self.win, text="✕", fg="#ef4444", bg="#18181b",
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        self.close_btn.bind("<Button-1>", lambda e: self._on_close_clicked())

        # Dedicated Resize Grip Widget (Bottom-Right, 24x24 px with resize cursor)
        self.grip = tk.Label(
            self.win, text="⤡", fg="#3b82f6", bg="#18181b",
            font=("Segoe UI", 12, "bold"), cursor="size_nw_se"
        )
        self.grip.bind("<Button-1>", self._on_resize_start)
        self.grip.bind("<B1-Motion>", self._on_resize_motion)
        self.grip.bind("<ButtonRelease-1>", self._on_resize_end)

        # Listen to window configure event for smooth redraw
        self.win.bind("<Configure>", self._on_window_configure)

        self._render_content()

    def _render_content(self):
        w = max(180, self.win.winfo_width())
        h = max(40, self.win.winfo_height())

        if not self.is_locked:
            # === EDIT MODE ===
            # Accent color matches selected style
            if self.style == "warning":
                border_color = "#eab308"
                badge_icon = "⚠️"
                accent_fg = "#fde047"
            elif self.style == "pure_black":
                border_color = "#71717a"
                badge_icon = "⬛"
                accent_fg = "#e4e4e7"
            elif self.style == "frosted":
                border_color = "#06b6d4"
                badge_icon = "🔲"
                accent_fg = "#67e8f9"
            else:  # redacted
                border_color = "#3b82f6"
                badge_icon = "🔒"
                accent_fg = "#93c5fd"

            bg_color = "#18181b"
            self.canvas.configure(bg=bg_color)

            # Update border
            self.canvas.coords(self.bg_rect_id, 1, 1, w - 2, h - 2)
            self.canvas.itemconfigure(self.bg_rect_id, fill=bg_color, outline=border_color, width=2, dash=(6, 4))

            # Header Badge
            badge_text = f"{badge_icon} 防窥条 #{self.mask_id} [{self.label_text}] • {self.style.upper()}"
            self.canvas.coords(self.header_text_id, 10, 16)
            self.canvas.itemconfigure(self.header_text_id, text=badge_text, fill=accent_fg, state="normal")

            # Center Hint
            self.canvas.coords(self.center_text_id, w // 2, h // 2 + 5)
            self.canvas.itemconfigure(
                self.center_text_id,
                text="[ 拖动移动 | 右下角⤡调大小 | 按 Ctrl+Alt+C 锁定穿透 ]",
                fill="#71717a", font=("Segoe UI", 9), state="normal"
            )

            # Show Interactive Widgets
            self.close_btn.configure(bg=bg_color)
            self.close_btn.place(relx=1.0, rely=0.0, anchor="ne", width=24, height=24)

            self.grip.configure(bg=bg_color, fg=border_color)
            self.grip.place(relx=1.0, rely=1.0, anchor="se", width=24, height=24)

        else:
            # === LOCKED MODE (CENSOR / REDACTED BAR) ===
            self.close_btn.place_forget()
            self.grip.place_forget()

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
            elif self.style == "frosted":
                bg_color = "#1e1e24"
                border_color = "#3f3f46"
                text_color = "#67e8f9"
                banner_text = f"🔲 [ FROSTED CENSOR • {self.label_text.upper()} ]"
            else:  # "redacted"
                bg_color = "#09090b"
                border_color = "#27272a"
                text_color = "#d4af37"
                banner_text = f"🔒 [ SENSITIVE DATA REDACTED • {self.label_text.upper()} ]"

            self.canvas.configure(bg=bg_color)
            self.canvas.coords(self.bg_rect_id, 0, 0, w, h)
            self.canvas.itemconfigure(self.bg_rect_id, fill=bg_color, outline=border_color, width=1, dash=())

            self.canvas.itemconfigure(self.header_text_id, state="hidden")

            if self.is_peeking:
                banner_text = f"👁️ [ PEEING • 临时透视中 • {self.label_text.upper()} ]"
                text_color = "#38bdf8"
                border_color = "#0284c7"

            self.canvas.coords(self.center_text_id, w // 2, h // 2)
            self.canvas.itemconfigure(
                self.center_text_id,
                text=banner_text, fill=text_color,
                font=("Consolas", 10, "bold"), state="normal"
            )

    def set_alpha(self, alpha: float):
        self.base_alpha = alpha
        if not self.is_peeking:
            self.win.wm_attributes("-alpha", alpha)

    def set_peeking(self, peeking: bool):
        self.is_peeking = peeking
        if peeking:
            # 20% alpha -> text underneath is clearly readable!
            self.win.wm_attributes("-alpha", 0.20)
        else:
            self.win.wm_attributes("-alpha", self.base_alpha)
        self._render_content()

    def _on_window_configure(self, event):
        if event.widget == self.win:
            w = max(180, self.win.winfo_width())
            h = max(40, self.win.winfo_height())
            if not self.is_locked:
                self.canvas.coords(self.bg_rect_id, 1, 1, w - 2, h - 2)
                self.canvas.coords(self.center_text_id, w // 2, h // 2 + 5)
            else:
                self.canvas.coords(self.bg_rect_id, 0, 0, w, h)
                self.canvas.coords(self.center_text_id, w // 2, h // 2)

    def set_locked(self, locked: bool):
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

    # Drag Handlers (Window Move)
    def _on_drag_start(self, event):
        if self.is_locked:
            return
        self._drag_data["x"] = event.x_root - self.win.winfo_x()
        self._drag_data["y"] = event.y_root - self.win.winfo_y()

    def _on_drag_motion(self, event):
        if self.is_locked:
            return
        new_x = event.x_root - self._drag_data["x"]
        new_y = event.y_root - self._drag_data["y"]
        self.win.geometry(f"+{new_x}+{new_y}")

    # Resize Handlers (Smooth Corner Drag)
    def _on_resize_start(self, event):
        if self.is_locked:
            return
        self._resize_data["x"] = event.x_root
        self._resize_data["y"] = event.y_root
        self._resize_data["w"] = self.win.winfo_width()
        self._resize_data["h"] = self.win.winfo_height()
        return "break"

    def _on_resize_motion(self, event):
        if self.is_locked:
            return
        dw = event.x_root - self._resize_data["x"]
        dh = event.y_root - self._resize_data["y"]
        new_w = max(180, self._resize_data["w"] + dw)
        new_h = max(40, self._resize_data["h"] + dh)
        self.win.geometry(f"{new_w}x{new_h}")
        return "break"

    def _on_resize_end(self, event):
        self._render_content()
        return "break"

    def _on_close_clicked(self):
        self.destroy()
        if self.on_close:
            self.on_close(self)

    def destroy(self):
        try:
            self.win.destroy()
        except Exception:
            pass
