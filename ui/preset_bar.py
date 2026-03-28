"""
PromptForge — ui/preset_bar.py
Preset bar UI: chips, save, export, import.
by daGonen
"""

import json
from tkinter import filedialog, messagebox
import customtkinter as ctk
from config import *
from data.presets import save_presets


class PresetBar(ctk.CTkFrame):
    def __init__(self, master, get_state, set_state, get_mode, **kwargs):
        """
        Args:
            get_state: callable() -> dict with keys: mode, model, blocks, vals, priorities
            set_state: callable(state: dict) -> None  — loads a preset into the app
            get_mode:  callable() -> str  — returns current active mode
        """
        super().__init__(master, fg_color=BG3, corner_radius=0, height=36, **kwargs)
        self.get_state = get_state
        self.set_state = set_state
        self.get_mode = get_mode
        self.presets = {}
        self.active_preset = None
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="presets /", text_color=TEXT3,
                     font=("Courier New", 9)).pack(side="left", padx=(10, 6), pady=8)

        self.chips_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chips_frame.pack(side="left", fill="x", expand=True)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=6)

        for label, cmd in [
            ("+ save",   self._save_dialog),
            ("export ↓", self._export),
            ("import ↑", self._import),
        ]:
            ctk.CTkButton(
                btn_frame, text=label, width=58, height=22,
                fg_color="transparent", text_color=TEXT3,
                border_width=1, border_color=BORDER,
                hover_color=BG4, corner_radius=5,
                font=FONT_SANS_XS, command=cmd
            ).pack(side="left", padx=2, pady=6)

    def load(self, presets: dict, mode: str, active_preset=None):
        """Refresh chips for the given mode."""
        self.presets = presets
        self.active_preset = active_preset
        self._render_chips(mode)

    def _render_chips(self, mode: str):
        for w in self.chips_frame.winfo_children():
            w.destroy()
        ps = self.presets.get(mode, [])
        for i, p in enumerate(ps):
            is_active = self.active_preset == i
            btn = ctk.CTkButton(
                self.chips_frame, text=p["name"], width=-1, height=22,
                fg_color=PURPLE_B if is_active else "transparent",
                text_color=PURPLE if is_active else TEXT2,
                border_width=1,
                border_color=PURPLE if is_active else BORDER,
                hover_color=BG4, corner_radius=20,
                font=FONT_SANS_SM,
                command=lambda x=i: self._load(x)
            )
            btn.pack(side="left", padx=2, pady=6)
            btn.bind("<Double-Button-1>", lambda e, x=i: self._delete(x))

    def _load(self, i: int):
        mode = self.get_mode()
        p = self.presets.get(mode, [])[i]
        self.active_preset = i
        self.set_state(p)
        self._render_chips(mode)

    def _save_dialog(self):
        dialog = ctk.CTkInputDialog(text="Preset name:", title="Save Preset")
        name = dialog.get_input()
        if not name or not name.strip():
            return
        name = name.strip()
        state = self.get_state()
        mode = state["mode"]
        new_preset = {
            "name": name,
            "model": state["model"],
            "blocks": list(state["blocks"]),
            "vals": {k: dict(v) for k, v in state["vals"].items() if k in state["blocks"]},
            "priorities": {k: v for k, v in state["priorities"].items()
                           if v != "auto" and k in state["blocks"]},
        }
        if mode not in self.presets:
            self.presets[mode] = []
        self.presets[mode].append(new_preset)
        self.active_preset = len(self.presets[mode]) - 1
        save_presets(self.presets)
        self._render_chips(mode)

    def _delete(self, i: int):
        mode = self.get_mode()
        p = self.presets.get(mode, [])[i]
        if messagebox.askyesno("Delete preset", f'Delete "{p["name"]}"?'):
            self.presets[mode].pop(i)
            if self.active_preset == i:
                self.active_preset = None
            elif self.active_preset and self.active_preset > i:
                self.active_preset -= 1
            save_presets(self.presets)
            self._render_chips(mode)

    def _export(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="promptforge-presets.json",
            title="Export Presets"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"Presets saved to:\n{path}")

    def _import(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Presets"
        )
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for m, ps in data.items():
                if m not in self.presets:
                    self.presets[m] = []
                for p in ps:
                    if not any(x["name"] == p["name"] for x in self.presets[m]):
                        self.presets[m].append(p)
            save_presets(self.presets)
            self._render_chips(self.get_mode())
            messagebox.showinfo("Imported", "Presets imported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import presets:\n{e}")
