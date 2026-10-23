"""
ScreenCloak Main Application: Floating Dock Controller & Window Manager.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import ctypes
import os
import sys
from typing import List, Dict, Any

from .mask import PrivacyMask
from .hotkeys import GlobalHotkeyManager, MOD_ALT, MOD_CONTROL
from .presets import load_presets, save_presets

class ScreenCloakApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScreenCloak Controller")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        # Place Dock near top center of screen
        screen_w = self.root.winfo_screenwidth()
        dock_w = 560
        dock_h = 42
        dock_x = (screen_w - dock_w) // 2
        dock_y = 24
        self.root.geometry(f"{dock_w}x{dock_h}+{dock_x}+{dock_y}")

        self.masks: List[PrivacyMask] = []
        self.mask_counter = 1
        self.is_locked = False
        self.is_peeking = False
        self.all_visible = True
        self.current_style = "redacted"
        self.current_alpha = 1.0  # 1.0 (100%), 0.85 (85%), 0.70 (70%)

        self.presets = load_presets()

        self._drag_data = {"x": 0, "y": 0}

        self._build_dock_ui()
        self._init_hotkeys()

        # Create one initial default privacy bar
        self.root.after(100, lambda: self.add_mask(dock_x - 50, dock_y + 120, 380, 65, "PASSWORD / SECRET"))

    def _build_dock_ui(self):
        # Dark Cyber Minimalist Dock
        bg_dock = "#09090b"
        border_dock = "#27272a"
        fg_text = "#f4f4f5"

        self.dock_frame = tk.Frame(self.root, bg=bg_dock, highlightbackground=border_dock, highlightthickness=1)
        self.dock_frame.pack(fill=tk.BOTH, expand=True)

        # Left Drag Handle
        self.handle_lbl = tk.Label(
            self.dock_frame, text=" ⠿ ", bg=bg_dock, fg="#71717a",
            font=("Segoe UI", 11, "bold"), cursor="fleur"
        )
        self.handle_lbl.pack(side=tk.LEFT, padx=(4, 0))
        self.handle_lbl.bind("<Button-1>", self._on_dock_drag_start)
        self.handle_lbl.bind("<B1-Motion>", self._on_dock_drag_motion)

        # Logo / Title
        self.title_lbl = tk.Label(
            self.dock_frame, text="🛡️ScreenCloak", bg=bg_dock, fg="#60a5fa",
            font=("Segoe UI", 9, "bold")
        )
        self.title_lbl.pack(side=tk.LEFT, padx=(2, 6))

        # Status Pill Button (Toggle Lock / Click-Through)
        self.status_btn = tk.Button(
            self.dock_frame, text="🔓 编辑中", bg="#854d0e", fg="#fef08a",
            activebackground="#a16207", activeforeground="#fef08a",
            font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=6, pady=1,
            command=self.toggle_lock
        )
        self.status_btn.pack(side=tk.LEFT, padx=3)

        # Peek Button (Quick Translucent View)
        self.peek_btn = tk.Button(
            self.dock_frame, text="👁️ 偷瞄", bg="#27272a", fg=fg_text,
            activebackground="#0284c7", activeforeground="#ffffff",
            font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=6, pady=1,
            command=self.toggle_peek
        )
        self.peek_btn.pack(side=tk.LEFT, padx=3)

        # Alpha Cycle Button (Opacity Level)
        self.alpha_btn = tk.Button(
            self.dock_frame, text="🌓 100%", bg="#27272a", fg=fg_text,
            activebackground="#3f3f46", activeforeground=fg_text,
            font=("Segoe UI", 8), relief=tk.FLAT, padx=5, pady=1,
            command=self.cycle_alpha
        )
        self.alpha_btn.pack(side=tk.LEFT, padx=3)

        # Quick Add Button
        self.add_btn = tk.Button(
            self.dock_frame, text="➕ 新建", bg="#27272a", fg=fg_text,
            activebackground="#3f3f46", activeforeground=fg_text,
            font=("Segoe UI", 8), relief=tk.FLAT, padx=6, pady=1,
            command=self.quick_add_mask
        )
        self.add_btn.pack(side=tk.LEFT, padx=3)

        # Draw to Add Button (Snipping Tool style)
        self.draw_btn = tk.Button(
            self.dock_frame, text="🎯 划框", bg="#27272a", fg=fg_text,
            activebackground="#3f3f46", activeforeground=fg_text,
            font=("Segoe UI", 8), relief=tk.FLAT, padx=6, pady=1,
            command=self.start_draw_mask
        )
        self.draw_btn.pack(side=tk.LEFT, padx=3)

        # Style Menu Button (Dropdown Popup)
        self.style_btn = tk.Button(
            self.dock_frame, text="🎨 样式 ▾", bg="#27272a", fg=fg_text,
            activebackground="#3f3f46", activeforeground=fg_text,
            font=("Segoe UI", 8), relief=tk.FLAT, padx=6, pady=1,
            command=self.show_style_menu
        )
        self.style_btn.pack(side=tk.LEFT, padx=3)

        # Presets Button
        self.preset_btn = tk.Button(
            self.dock_frame, text="📋 预设", bg="#27272a", fg=fg_text,
            activebackground="#3f3f46", activeforeground=fg_text,
            font=("Segoe UI", 8), relief=tk.FLAT, padx=6, pady=1,
            command=self.show_preset_menu
        )
        self.preset_btn.pack(side=tk.LEFT, padx=3)

        # Eye / Visibility Toggle Button
        self.vis_btn = tk.Button(
            self.dock_frame, text="👁️", bg="#27272a", fg=fg_text,
            activebackground="#3f3f46", activeforeground=fg_text,
            font=("Segoe UI", 8), relief=tk.FLAT, padx=4, pady=1,
            command=self.toggle_all_visibility
        )
        self.vis_btn.pack(side=tk.LEFT, padx=3)

        # Close App Button
        self.close_btn = tk.Button(
            self.dock_frame, text="✕", bg="#27272a", fg="#ef4444",
            activebackground="#991b1b", activeforeground="#ffffff",
            font=("Segoe UI", 8, "bold"), relief=tk.FLAT, padx=6, pady=1,
            command=self.exit_app
        )
        self.close_btn.pack(side=tk.RIGHT, padx=(2, 6))

    def _init_hotkeys(self):
        self.hotkey_mgr = GlobalHotkeyManager()
        # Ctrl+Alt+C: Toggle Lock / Pass-Through
        self.hotkey_mgr.register(MOD_CONTROL | MOD_ALT, 0x43, lambda: self.root.after(0, self.toggle_lock))
        # Ctrl+Alt+V: Toggle Peek (Quick Translucent View of Code)
        self.hotkey_mgr.register(MOD_CONTROL | MOD_ALT, 0x56, lambda: self.root.after(0, self.toggle_peek))
        # Ctrl+Alt+N: New Mask
        self.hotkey_mgr.register(MOD_CONTROL | MOD_ALT, 0x4E, lambda: self.root.after(0, self.quick_add_mask))
        # Ctrl+Alt+H: Toggle Visibility
        self.hotkey_mgr.register(MOD_CONTROL | MOD_ALT, 0x48, lambda: self.root.after(0, self.toggle_all_visibility))
        self.hotkey_mgr.start()

    def add_mask(self, x: int, y: int, w: int, h: int, label: str = "CONFIDENTIAL"):
        mask = PrivacyMask(
            master=self.root,
            mask_id=self.mask_counter,
            x=x, y=y, width=w, height=h,
            label=label,
            style=self.current_style,
            on_close=self._on_mask_removed
        )
        mask.set_locked(self.is_locked)
        self.masks.append(mask)
        self.mask_counter += 1

    def quick_add_mask(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        # Spawn near center with slight cascade
        offset = (len(self.masks) * 25) % 200
        x = (screen_w - 380) // 2 + offset
        y = (screen_h - 65) // 2 + offset
        self.add_mask(x, y, 380, 65, "TOKEN / SECRET")

    def _on_mask_removed(self, mask: PrivacyMask):
        if mask in self.masks:
            self.masks.remove(mask)

    def toggle_lock(self):
        """
        Toggles between Edit Mode and Locked (Click-through) mode.
        """
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.status_btn.configure(text="🔒 已穿透锁定", bg="#15803d", fg="#bbf7d0", activebackground="#166534")
        else:
            self.status_btn.configure(text="🔓 编辑中", bg="#854d0e", fg="#fef08a", activebackground="#a16207")

        for m in self.masks:
            m.set_locked(self.is_locked)

    def toggle_peek(self):
        """
        Toggles temporary translucency so user can peek at what is underneath.
        """
        self.is_peeking = not self.is_peeking
        if self.is_peeking:
            self.peek_btn.configure(text="👁️ 偷瞄中", bg="#0284c7", fg="#ffffff")
        else:
            self.peek_btn.configure(text="👁️ 偷瞄", bg="#27272a", fg="#f4f4f5")

        for m in self.masks:
            m.set_peeking(self.is_peeking)

    def cycle_alpha(self):
        """
        Cycles base opacity: 100% -> 85% -> 70%
        85% allows the presenter to see their code on high-res screen,
        while Zoom/Tencent Meeting video compression crushes it into an illegible dark block!
        """
        alpha_levels = [(1.0, "🌓 100%"), (0.85, "🌓 85%"), (0.70, "🌓 70%")]
        current_idx = 0
        for i, (val, _) in enumerate(alpha_levels):
            if abs(self.current_alpha - val) < 0.01:
                current_idx = i
                break

        next_idx = (current_idx + 1) % len(alpha_levels)
        self.current_alpha, label = alpha_levels[next_idx]
        self.alpha_btn.configure(text=label)

        for m in self.masks:
            m.set_alpha(self.current_alpha)

    def show_style_menu(self):
        """
        Pops up an explicit style selection dropdown menu.
        """
        menu = tk.Menu(
            self.root, tearoff=0, bg="#18181b", fg="#f4f4f5",
            activebackground="#3b82f6", activeforeground="#ffffff",
            font=("Segoe UI", 9)
        )
        styles = [
            ("redacted", "🔒 绝密黑金 (Redacted Obsidian)"),
            ("warning", "⚠️ 高危警示 (Warning Classified)"),
            ("pure_black", "⬛ 纯黑哑光 (Pure Blackout)"),
            ("frosted", "🔲 磨砂深灰 (Frosted Charcoal)")
        ]
        for style_key, label in styles:
            is_checked = (self.current_style == style_key)
            prefix = "✓ " if is_checked else "   "
            menu.add_command(
                label=f"{prefix}{label}",
                command=lambda s=style_key: self.select_style(s)
            )

        # Popup just below the Style button
        bx = self.style_btn.winfo_rootx()
        by = self.style_btn.winfo_rooty() + self.style_btn.winfo_height() + 4
        menu.tk_popup(bx, by)

    def select_style(self, style_name: str):
        self.current_style = style_name
        for m in self.masks:
            m.set_style(self.current_style)

    def toggle_all_visibility(self):
        self.all_visible = not self.all_visible
        for m in self.masks:
            m.set_visible(self.all_visible)
        if self.all_visible:
            self.vis_btn.configure(text="👁️", fg="#f4f4f5")
        else:
            self.vis_btn.configure(text="🚫", fg="#ef4444")

    # Draw to Add (Snipping Tool Style)
    def start_draw_mask(self):
        """
        Opens a transparent full-screen overlay for user to drag and draw a privacy mask.
        """
        snip = tk.Toplevel(self.root)
        snip.overrideredirect(True)
        snip.wm_attributes("-topmost", True)
        snip.wm_attributes("-alpha", 0.3)
        snip.configure(bg="#000000")
        snip.geometry(f"{snip.winfo_screenwidth()}x{snip.winfo_screenheight()}+0+0")

        canvas = tk.Canvas(snip, cursor="cross", bg="#000000", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        start_pt = {"x": 0, "y": 0}
        rect_id = None

        def on_down(e):
            nonlocal rect_id
            start_pt["x"] = e.x
            start_pt["y"] = e.y
            rect_id = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="#38bdf8", width=2, fill="#0284c7")

        def on_move(e):
            if rect_id:
                canvas.coords(rect_id, start_pt["x"], start_pt["y"], e.x, e.y)

        def on_up(e):
            x1 = min(start_pt["x"], e.x)
            y1 = min(start_pt["y"], e.y)
            x2 = max(start_pt["x"], e.x)
            y2 = max(start_pt["y"], e.y)
            w = max(120, x2 - x1)
            h = max(35, y2 - y1)
            snip.destroy()
            self.add_mask(x1, y1, w, h, "PROTECTED_DATA")

        def on_cancel(e):
            snip.destroy()

        canvas.bind("<Button-1>", on_down)
        canvas.bind("<B1-Motion>", on_move)
        canvas.bind("<ButtonRelease-1>", on_up)
        snip.bind("<Escape>", on_cancel)

    # Preset Menu
    def show_preset_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#18181b", fg="#f4f4f5", activebackground="#3b82f6")
        menu.add_command(label="💾 保存当前布局为新预设...", command=self.save_current_as_preset)
        menu.add_separator()

        for name in self.presets.keys():
            menu.add_command(
                label=f"📂 载入: {name}",
                command=lambda n=name: self.load_preset(n)
            )

        menu.tk_popup(self.preset_btn.winfo_rootx(), self.preset_btn.winfo_rooty() + 32)

    def save_current_as_preset(self):
        name = simpledialog.askstring("保存预设", "请输入预设名称（例如：VS Code 开会）:", parent=self.root)
        if not name:
            return
        layout = [m.get_geometry() for m in self.masks]
        self.presets[name] = layout
        save_presets(self.presets)
        messagebox.showinfo("成功", f"预设 '{name}' 已保存！", parent=self.root)

    def load_preset(self, name: str):
        if name not in self.presets:
            return
        # Clear existing
        for m in list(self.masks):
            m.destroy()
        self.masks.clear()

        layout = self.presets[name]
        for item in layout:
            self.add_mask(
                item.get("x", 200),
                item.get("y", 200),
                item.get("w", 360),
                item.get("h", 65),
                item.get("label", "SECRET")
            )

    # Dock Window Movement
    def _on_dock_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_dock_drag_motion(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        new_x = self.root.winfo_x() + dx
        new_y = self.root.winfo_y() + dy
        self.root.geometry(f"+{new_x}+{new_y}")

    def exit_app(self):
        self.hotkey_mgr.stop()
        for m in self.masks:
            m.destroy()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()
