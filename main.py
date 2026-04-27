import customtkinter as ctk
import pyautogui
import keyboard
import threading
import time
import sys
import os
import ctypes
import json

# --- Appearance ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Colors
ACCENT       = "#6c5ce7"
ACCENT_HOVER = "#5a4bd1"
GREEN        = "#2dc653"
GREEN_HOVER  = "#25a244"
RED          = "#e63946"
RED_HOVER    = "#c1121f"
MUTED        = "#6c757d"
BG_DARK      = "#111122"
CARD_BG      = "#1a1a35"
INPUT_BG     = "#0f3460"

DEFAULT_SETTINGS = {
    "spammer": {"start": "f6", "stop": "f7"},
    "clicker": {"start": "f3", "stop": "f4"},
    "holder": {"start": "f1", "stop": "f2"},
    "afk": {"start": "f8", "stop": "f9"}
}


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings - Hotkeys")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)
        
        icon_path = parent._resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Make it modal
        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(
            self, text="⚙ Rebind Hotkeys",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#e0e0ff"
        ).grid(row=0, column=0, columnspan=2, pady=(20, 15))

        self.temp_config = {
            "spammer": self.parent.config["spammer"].copy(),
            "clicker": self.parent.config["clicker"].copy(),
            "holder":  self.parent.config["holder"].copy(),
            "afk":     self.parent.config["afk"].copy()
        }

        self.btn_refs = {}

        # Build rows
        categories = [
            ("Spammer", "spammer"),
            ("Clicker", "clicker"),
            ("Holder", "holder"),
            ("Anti-AFK", "afk")
        ]

        # Layout settings container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, columnspan=2, padx=20, sticky="nsew")

        for i, (name, key) in enumerate(categories):
            ctk.CTkLabel(container, text=name, font=ctk.CTkFont(size=14, weight="bold"), text_color="#b0b0cc", width=80, anchor="w").grid(row=i, column=0, pady=8, padx=(0, 20))
            
            start_btn = ctk.CTkButton(container, text=self.temp_config[key]["start"].upper(), width=100,
                                      fg_color=INPUT_BG, hover_color=ACCENT_HOVER, border_width=1, border_color=ACCENT)
            start_btn.grid(row=i, column=1, padx=10, pady=8)
            start_btn.configure(command=lambda k=key, f="start", b=start_btn: self._listen_for_key(k, f, b))
            
            stop_btn = ctk.CTkButton(container, text=self.temp_config[key]["stop"].upper(), width=100,
                                     fg_color=INPUT_BG, hover_color=ACCENT_HOVER, border_width=1, border_color=RED)
            stop_btn.grid(row=i, column=2, padx=10, pady=8)
            stop_btn.configure(command=lambda k=key, f="stop", b=stop_btn: self._listen_for_key(k, f, b))

        self.status_label = ctk.CTkLabel(self, text="", text_color="#ffd166", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Bottom buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(15, 20))

        ctk.CTkButton(btn_frame, text="Save Settings", width=120, height=36, fg_color=GREEN, hover_color=GREEN_HOVER, font=ctk.CTkFont(weight="bold"),
                      command=self._save_settings).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, height=36, fg_color=MUTED, hover_color="#5a6268", font=ctk.CTkFont(weight="bold"),
                      command=self.destroy).pack(side="left", padx=10)

        self._listening = False

    def _listen_for_key(self, tool_key, btn_func, button_widget):
        if self._listening: return
        self._listening = True
        original_text = button_widget.cget("text")
        button_widget.configure(text="...", fg_color="#ffd166", text_color="#111122")
        self.status_label.configure(text="Press any key to assign...")
        
        def listener():
            event = keyboard.read_event(suppress=False)
            while event.event_type != keyboard.KEY_DOWN:
                event = keyboard.read_event(suppress=False)
            
            new_key = event.name.lower()
            self.temp_config[tool_key][btn_func] = new_key
            
            def update_ui():
                button_widget.configure(text=new_key.upper(), fg_color=INPUT_BG, text_color="white")
                self.status_label.configure(text="")
                self._listening = False
            
            self.after(0, update_ui)
            
        threading.Thread(target=listener, daemon=True).start()

    def _save_settings(self):
        if self._listening: return
        self.parent.update_config(self.temp_config)
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("AutoInput")
        self.geometry("520x470")
        self.resizable(False, False)
        self.attributes("-topmost", True)

        icon_path = self._resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        self.configure(fg_color=BG_DARK)
        
        # Load Settings
        self.settings_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "settings.json")
        self.config = self._load_config()

        # --- State flags ---
        self.is_spamming = False
        self.is_clicking = False
        self.is_holding = False
        self.is_afk = False
        self._listening_for_key = False

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="⚡ AutoInput",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#e0e0ff"
        ).grid(row=0, column=0, sticky="w")
        
        settings_btn = ctk.CTkButton(
            header, text="⚙ Settings", width=80, height=26,
            fg_color=INPUT_BG, hover_color=ACCENT_HOVER, corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"), command=self.open_settings
        )
        settings_btn.grid(row=0, column=1, sticky="e")

        # --- Tabview ---
        self.tabs = ctk.CTkTabview(
            self, fg_color=CARD_BG,
            segmented_button_fg_color="#0d0d2b",
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color="#0d0d2b",
            segmented_button_unselected_hover_color="#1a1a40",
            corner_radius=12
        )
        self.tabs.grid(row=1, column=0, padx=16, pady=(4, 6), sticky="nsew")

        self.tabs.add("  Spammer  ")
        self.tabs.add("  Clicker  ")
        self.tabs.add("  Holder  ")
        self.tabs.add("  Anti-AFK  ")

        self._build_spammer_tab(self.tabs.tab("  Spammer  "))
        self._build_clicker_tab(self.tabs.tab("  Clicker  "))
        self._build_holder_tab(self.tabs.tab("  Holder  "))
        self._build_afk_tab(self.tabs.tab("  Anti-AFK  "))

        # --- Footer ---
        self.footer_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11), text_color=MUTED
        )
        self.footer_label.grid(row=2, column=0, padx=20, pady=(0, 12))

        self._refresh_ui_labels()
        self._bind_hotkeys()

    # ─── Config & Hotkeys ──────────────────────────────────
    def _load_config(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    data = json.load(f)
                    
                    # Validate all keys exist, fallback if incomplete or dirty
                    for k1, v1 in DEFAULT_SETTINGS.items():
                        if k1 not in data: data[k1] = {}
                        for k2, v2 in v1.items():
                            if k2 not in data[k1]: data[k1][k2] = v2
                    return data
            except Exception:
                pass
        return json.loads(json.dumps(DEFAULT_SETTINGS))

    def _save_config(self):
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def update_config(self, new_config):
        self.config = new_config
        self._save_config()
        self._refresh_ui_labels()
        self._bind_hotkeys()

    def _bind_hotkeys(self):
        if not hasattr(self, '_hotkey_refs'):
            self._hotkey_refs = []
        for ref in self._hotkey_refs:
            try: keyboard.remove_hotkey(ref)
            except Exception: pass
        self._hotkey_refs.clear()
        
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['spammer']['start'], self._start_spamming))
        except ValueError: pass
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['spammer']['stop'], self._stop_spamming))
        except ValueError: pass
        
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['clicker']['start'], self._start_clicking))
        except ValueError: pass
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['clicker']['stop'], self._stop_clicking))
        except ValueError: pass
        
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['holder']['start'], self._start_holding))
        except ValueError: pass
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['holder']['stop'], self._stop_holding))
        except ValueError: pass
        
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['afk']['start'], self._start_afk))
        except ValueError: pass
        try: self._hotkey_refs.append(keyboard.add_hotkey(self.config['afk']['stop'], self._stop_afk))
        except ValueError: pass

    def _refresh_ui_labels(self):
        h = self.config['holder']
        c = self.config['clicker']
        s = self.config['spammer']
        a = self.config['afk']
        
        self.footer_label.configure(text=f"F-Hotkeys: Holder ({h['start'].upper()}/{h['stop'].upper()}) · Clicker ({c['start'].upper()}/{c['stop'].upper()}) · Spammer ({s['start'].upper()}/{s['stop'].upper()}) · AFK ({a['start'].upper()}/{a['stop'].upper()})")
        
        self._controls_refs['spammer_start'].configure(text=f"▶  Start ({s['start'].upper()})")
        self._controls_refs['spammer_stop'].configure(text=f"■  Stop ({s['stop'].upper()})")
        
        self._controls_refs['clicker_start'].configure(text=f"▶  Start ({c['start'].upper()})")
        self._controls_refs['clicker_stop'].configure(text=f"■  Stop ({c['stop'].upper()})")
        
        self._controls_refs['holder_start'].configure(text=f"▶  Start ({h['start'].upper()})")
        self._controls_refs['holder_stop'].configure(text=f"■  Stop ({h['stop'].upper()})")
        
        self._controls_refs['afk_start'].configure(text=f"▶  Start ({a['start'].upper()})")
        self._controls_refs['afk_stop'].configure(text=f"■  Stop ({a['stop'].upper()})")

    def open_settings(self):
        if not hasattr(self, "settings_window") or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        self.settings_window.focus()


    # ─── Helpers ────────────────────────────────────────────
    @staticmethod
    def _resource_path(relative_path):
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, relative_path)

    def _make_controls(self, parent, row, start_cmd, stop_cmd, key_start, key_stop):
        if not hasattr(self, '_controls_refs'):
            self._controls_refs = {}
            
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=row, column=0, padx=16, pady=(14, 6))

        start_btn = ctk.CTkButton(
            btn_frame, text=f"▶  Start ({self.config[key_start][key_stop].upper()})", width=140, height=36,
            fg_color=GREEN, hover_color=GREEN_HOVER, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"), command=start_cmd
        )
        start_btn.pack(side="left", padx=8)
        self._controls_refs[key_start + "_start"] = start_btn

        stop_btn = ctk.CTkButton(
            btn_frame, text=f"■  Stop ({self.config[key_start][key_stop].upper()})", width=140, height=36,
            fg_color=RED, hover_color=RED_HOVER, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"), command=stop_cmd,
            state="disabled"
        )
        stop_btn.pack(side="left", padx=8)
        self._controls_refs[key_start + "_stop"] = stop_btn

        status = ctk.CTkLabel(parent, text="● Idle", text_color=MUTED, font=ctk.CTkFont(size=12))
        status.grid(row=row + 1, column=0, padx=16, pady=(2, 8))

        return start_btn, stop_btn, status

    # ═══════════════════════════════════════════════════════
    #  TAB 1: AUTO SPAMMER
    # ═══════════════════════════════════════════════════════
    def _build_spammer_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        self.spam_text_entry = ctk.CTkEntry(tab, placeholder_text="Enter text to spam…", width=320, height=36, corner_radius=8)
        self.spam_text_entry.grid(row=0, column=0, padx=16, pady=(16, 4))

        delay_frame = ctk.CTkFrame(tab, fg_color="transparent")
        delay_frame.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        ctk.CTkLabel(delay_frame, text="Delay (sec):", font=ctk.CTkFont(size=13), text_color="#b0b0cc").pack(side="left", padx=(0, 12))
        self.spam_delay_entry = ctk.CTkEntry(delay_frame, width=90, height=32, corner_radius=8)
        self.spam_delay_entry.insert(0, "0.1")
        self.spam_delay_entry.pack(side="right")

        self.spam_start, self.spam_stop, self.spam_status = self._make_controls(
            tab, 2, self._start_spamming, self._stop_spamming, "spammer", "start"
        )

    def _start_spamming(self):
        if self.is_spamming:
            return
        text = self.spam_text_entry.get()
        if not text:
            self.spam_status.configure(text="● Error — empty text", text_color=RED)
            return
        try:
            delay = float(self.spam_delay_entry.get())
        except ValueError:
            self.spam_status.configure(text="● Error — invalid delay", text_color=RED)
            return

        self.is_spamming = True
        self.spam_start.configure(state="disabled")
        self.spam_stop.configure(state="normal")
        self.spam_status.configure(text="● Spamming…", text_color=GREEN)
        self.spam_text_entry.configure(state="disabled")
        self.spam_delay_entry.configure(state="disabled")

        threading.Thread(target=self._spam_loop, args=(text, delay), daemon=True).start()

    def _stop_spamming(self):
        if not self.is_spamming:
            return
        self.is_spamming = False
        self.spam_start.configure(state="normal")
        self.spam_stop.configure(state="disabled")
        self.spam_status.configure(text="● Idle", text_color=MUTED)
        self.spam_text_entry.configure(state="normal")
        self.spam_delay_entry.configure(state="normal")

    def _spam_loop(self, text, delay):
        while self.is_spamming:
            pyautogui.typewrite(text)
            pyautogui.press('enter')
            time.sleep(delay)

    # ═══════════════════════════════════════════════════════
    #  TAB 2: AUTO CLICKER
    # ═══════════════════════════════════════════════════════
    def _build_clicker_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        # Click button
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=16, pady=(16, 6), sticky="ew")
        ctk.CTkLabel(btn_frame, text="Button:", font=ctk.CTkFont(size=13), text_color="#b0b0cc").pack(side="left", padx=(0, 12))
        self.click_button_var = ctk.StringVar(value="left")
        ctk.CTkOptionMenu(
            btn_frame, values=["left", "right", "middle"],
            variable=self.click_button_var, width=120, height=32,
            fg_color=INPUT_BG, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=8
        ).pack(side="right")

        # Click type
        type_frame = ctk.CTkFrame(tab, fg_color="transparent")
        type_frame.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        ctk.CTkLabel(type_frame, text="Click type:", font=ctk.CTkFont(size=13), text_color="#b0b0cc").pack(side="left", padx=(0, 12))
        self.click_type_var = ctk.StringVar(value="single")
        ctk.CTkOptionMenu(
            type_frame, values=["single", "double"],
            variable=self.click_type_var, width=120, height=32,
            fg_color=INPUT_BG, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            corner_radius=8
        ).pack(side="right")

        # Speed mode: Interval or CPS
        speed_frame = ctk.CTkFrame(tab, fg_color="transparent")
        speed_frame.grid(row=2, column=0, padx=16, pady=6, sticky="ew")

        self.click_speed_mode = ctk.StringVar(value="Interval")
        self.speed_mode_label = ctk.CTkLabel(speed_frame, text="Interval (sec):", font=ctk.CTkFont(size=13), text_color="#b0b0cc")
        self.speed_mode_label.pack(side="left", padx=(0, 8))

        self.click_speed_entry = ctk.CTkEntry(speed_frame, width=80, height=32, corner_radius=8)
        self.click_speed_entry.insert(0, "0.1")
        self.click_speed_entry.pack(side="right")

        self.speed_toggle_btn = ctk.CTkSegmentedButton(
            speed_frame, values=["Interval", "CPS"],
            variable=self.click_speed_mode,
            command=self._on_speed_mode_change,
            font=ctk.CTkFont(size=11),
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color="#0d0d2b", unselected_hover_color="#1a1a40",
            width=120, height=28, corner_radius=6
        )
        self.speed_toggle_btn.pack(side="right", padx=(0, 8))

        # Buttons
        self.click_start, self.click_stop, self.click_status = self._make_controls(
            tab, 3, self._start_clicking, self._stop_clicking, "clicker", "start"
        )

    def _on_speed_mode_change(self, mode):
        self.click_speed_entry.delete(0, "end")
        if mode == "CPS":
            self.speed_mode_label.configure(text="CPS:")
            self.click_speed_entry.insert(0, "10")
        else:
            self.speed_mode_label.configure(text="Interval (sec):")
            self.click_speed_entry.insert(0, "0.1")

    def _get_click_interval(self):
        """Convert the user input to an interval in seconds."""
        val = float(self.click_speed_entry.get())
        if val <= 0:
            raise ValueError("Value must be > 0")
        if self.click_speed_mode.get() == "CPS":
            return 1.0 / val
        return val

    def _start_clicking(self):
        if self.is_clicking:
            return
        try:
            interval = self._get_click_interval()
        except ValueError:
            self.click_status.configure(text="● Error — invalid value", text_color=RED)
            return

        self.is_clicking = True
        self.click_start.configure(state="disabled")
        self.click_stop.configure(state="normal")
        self.click_status.configure(text="● Clicking…", text_color=GREEN)
        self.click_speed_entry.configure(state="disabled")

        btn = self.click_button_var.get()
        clicks = 2 if self.click_type_var.get() == "double" else 1
        threading.Thread(target=self._click_loop, args=(btn, clicks, interval), daemon=True).start()

    def _stop_clicking(self):
        if not self.is_clicking:
            return
        self.is_clicking = False
        self.click_start.configure(state="normal")
        self.click_stop.configure(state="disabled")
        self.click_status.configure(text="● Idle", text_color=MUTED)
        self.click_speed_entry.configure(state="normal")

    # Win32 mouse event flags for direct, zero-overhead clicking
    _MOUSE_FLAGS = {
        "left":   (0x0002, 0x0004),  # LEFTDOWN, LEFTUP
        "right":  (0x0008, 0x0010),  # RIGHTDOWN, RIGHTUP
        "middle": (0x0020, 0x0040),  # MIDDLEDOWN, MIDDLEUP
    }

    def _click_loop(self, button, clicks, interval):
        down, up = self._MOUSE_FLAGS.get(button, (0x0002, 0x0004))
        mouse_event = ctypes.windll.user32.mouse_event
        perf = time.perf_counter
        next_click = perf()
        while self.is_clicking:
            now = perf()
            if now >= next_click:
                for _ in range(clicks):
                    mouse_event(down, 0, 0, 0, 0)
                    mouse_event(up, 0, 0, 0, 0)
                next_click += interval
                # If we fell behind, reset instead of burst-catching-up
                if next_click < now:
                    next_click = now + interval
            else:
                # Yield CPU briefly to avoid 100% core usage
                time.sleep(0.0005)

    # ═══════════════════════════════════════════════════════
    #  TAB 3: BUTTON HOLDER
    # ═══════════════════════════════════════════════════════
    def _build_holder_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        # Instructions
        ctk.CTkLabel(
            tab, text="Press the button below, then press\nany key or mouse button to select it.",
            font=ctk.CTkFont(size=12), text_color="#8888aa", justify="center"
        ).grid(row=0, column=0, padx=16, pady=(14, 6))

        # Detect button + display
        detect_frame = ctk.CTkFrame(tab, fg_color="transparent")
        detect_frame.grid(row=1, column=0, padx=16, pady=6)

        self.hold_key_display = ctk.CTkLabel(
            detect_frame, text="None",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#e0e0ff",
            width=120, height=36, corner_radius=8, fg_color=INPUT_BG
        )
        self.hold_key_display.pack(side="left", padx=(0, 12))

        self.detect_btn = ctk.CTkButton(
            detect_frame, text="🎯  Detect Key", width=140, height=36,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._start_key_detection
        )
        self.detect_btn.pack(side="left")

        self._selected_hold_key = None

        # Controls
        self.hold_start, self.hold_stop, self.hold_status = self._make_controls(
            tab, 2, self._start_holding, self._stop_holding, "holder", "start"
        )

    def _start_key_detection(self):
        """Listen for next keyboard/mouse press and capture it."""
        if self._listening_for_key:
            return
        self._listening_for_key = True
        self.detect_btn.configure(text="⏳  Press a key…", state="disabled", fg_color="#444466")
        self.hold_key_display.configure(text="…", text_color="#ffd166")

        threading.Thread(target=self._detect_key_thread, daemon=True).start()

    def _detect_key_thread(self):
        """Runs in a thread — waits for any key press."""
        event = keyboard.read_event(suppress=False)
        # Only react to key-down events
        while event.event_type != keyboard.KEY_DOWN:
            event = keyboard.read_event(suppress=False)

        key_name = event.name
        self._selected_hold_key = key_name
        self._listening_for_key = False

        # Update UI from main thread
        self.after(0, self._update_key_display, key_name)

    def _update_key_display(self, key_name):
        self.hold_key_display.configure(text=key_name.upper(), text_color="#2dc653")
        self.detect_btn.configure(text="🎯  Detect Key", state="normal", fg_color=ACCENT)

    def _start_holding(self):
        if self.is_holding:
            return
        if self._selected_hold_key is None:
            self.hold_status.configure(text="● Error — detect a key first", text_color=RED)
            return

        key = self._selected_hold_key
        self.is_holding = True
        self.hold_start.configure(state="disabled")
        self.hold_stop.configure(state="normal")
        self.hold_status.configure(text=f"● Holding '{key}'…", text_color=GREEN)
        self.detect_btn.configure(state="disabled")

        threading.Thread(target=self._hold_loop, args=(key,), daemon=True).start()

    def _stop_holding(self):
        if not self.is_holding:
            return
        self.is_holding = False
        self.hold_start.configure(state="normal")
        self.hold_stop.configure(state="disabled")
        self.hold_status.configure(text="● Idle", text_color=MUTED)
        self.detect_btn.configure(state="normal")

    def _hold_loop(self, key):
        # Emulate hardware auto-repeat by repeatedly sending the key-down event.
        # This ensures the key registers as "held" for both typing (aaaa...) and games.
        while self.is_holding:
            keyboard.press(key)
            time.sleep(0.03)
        keyboard.release(key)

    # ═══════════════════════════════════════════════════════
    #  TAB 4: ANTI-AFK
    # ═══════════════════════════════════════════════════════
    def _build_afk_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tab, text="Cycles W → S → A → D to keep\nyour character moving in place.",
            font=ctk.CTkFont(size=12), text_color="#8888aa", justify="center"
        ).grid(row=0, column=0, padx=16, pady=(14, 6))

        # Step duration
        dur_frame = ctk.CTkFrame(tab, fg_color="transparent")
        dur_frame.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        ctk.CTkLabel(dur_frame, text="Step duration (sec):", font=ctk.CTkFont(size=13), text_color="#b0b0cc").pack(side="left", padx=(0, 12))
        self.afk_duration_entry = ctk.CTkEntry(dur_frame, width=80, height=32, corner_radius=8)
        self.afk_duration_entry.insert(0, "0.5")
        self.afk_duration_entry.pack(side="right")

        # Controls
        self.afk_start, self.afk_stop, self.afk_status = self._make_controls(
            tab, 2, self._start_afk, self._stop_afk, "afk", "start"
        )

    def _start_afk(self):
        if self.is_afk:
            return
        try:
            duration = float(self.afk_duration_entry.get())
            if duration <= 0:
                raise ValueError
        except ValueError:
            self.afk_status.configure(text="● Error — invalid duration", text_color=RED)
            return

        self.is_afk = True
        self.afk_start.configure(state="disabled")
        self.afk_stop.configure(state="normal")
        self.afk_status.configure(text="● Anti-AFK active…", text_color=GREEN)
        self.afk_duration_entry.configure(state="disabled")

        threading.Thread(target=self._afk_loop, args=(duration,), daemon=True).start()

    def _stop_afk(self):
        if not self.is_afk:
            return
        self.is_afk = False
        self.afk_start.configure(state="normal")
        self.afk_stop.configure(state="disabled")
        self.afk_status.configure(text="● Idle", text_color=MUTED)
        self.afk_duration_entry.configure(state="normal")

    def _afk_loop(self, duration):
        # W/S cancel out (forward/back), A/D cancel out (left/right)
        keys = ['w', 's', 'a', 'd']
        idx = 0
        while self.is_afk:
            key = keys[idx % 4]
            keyboard.press(key)
            # Sleep in small chunks so we can stop quickly
            elapsed = 0.0
            while elapsed < duration and self.is_afk:
                time.sleep(0.05)
                elapsed += 0.05
            keyboard.release(key)
            idx += 1


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0
    app = App()
    app.mainloop()
