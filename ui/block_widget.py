"""
PromptForge — ui/block_widget.py
Self-contained BlockWidget component.

Fixes:
1. Range field label only renders when slider is visible — no ghost labels
2. Priority reset button appears next to badge when override is active
3. Field description font bumped to 11pt for readability

by daGonen
"""

import tkinter as tk
import customtkinter as ctk
from config import *
from data.modes import MODES
from core.assembler import model_supports_weights, weight_syntax_label


class BlockWidget(ctk.CTkFrame):
    def __init__(self, master, key: str, mode: str, vals: dict, priorities: dict,
                 on_change, on_remove, on_drag_start, on_drag_end,
                 on_move_up, on_move_down,
                 active_blocks: list, active_model: str, **kwargs):
        super().__init__(master, fg_color=BG2, corner_radius=8,
                         border_width=1, border_color=BORDER, **kwargs)

        self.key           = key
        self.mode          = mode
        self.vals          = vals
        self.priorities    = priorities
        self.on_change     = on_change
        self.on_remove     = on_remove
        self.on_drag_start = on_drag_start
        self.on_drag_end   = on_drag_end
        self.on_move_up    = on_move_up
        self.on_move_down  = on_move_down
        self.active_blocks = active_blocks
        self.active_model  = active_model
        self.expanded      = False
        self.field_widgets = {}
        self._weight_rows  = []   # refs to weight row frames for show/hide

        self._build()

    def _build(self):
        bdef = MODES[self.mode]["blocks"][self.key]
        core = MODES[self.mode]["core"]

        # ── Header ──────────────────────────────────────────────────────
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=8, pady=(6, 4))

        # Drag handle
        self.drag_handle = ctk.CTkLabel(
            self.header, text="⠿", text_color=TEXT3,
            font=("Courier New", 14), cursor="fleur", width=18
        )
        self.drag_handle.pack(side="left", padx=(0, 2))
        self.drag_handle.bind("<ButtonPress-1>",   self._on_drag_press)
        self.drag_handle.bind("<ButtonRelease-1>", self._on_drag_release)

        # Up / Down arrows
        ctk.CTkButton(
            self.header, text="↑", width=20, height=20,
            fg_color="transparent", text_color=TEXT3,
            hover_color=BG4, corner_radius=4,
            font=("Segoe UI", 11), command=self._move_up
        ).pack(side="left", padx=(0, 1))
        ctk.CTkButton(
            self.header, text="↓", width=20, height=20,
            fg_color="transparent", text_color=TEXT3,
            hover_color=BG4, corner_radius=4,
            font=("Segoe UI", 11), command=self._move_down
        ).pack(side="left", padx=(0, 6))

        # Icon
        icon = ctk.CTkLabel(self.header, text=bdef["icon"], text_color=TEXT2,
                            font=("Segoe UI", 12), width=20)
        icon.pack(side="left", padx=(0, 5))
        icon.bind("<Button-1>", self._toggle_handler)

        # Name
        name = ctk.CTkLabel(self.header, text=bdef["name"], text_color=TEXT,
                            font=FONT_BOLD, anchor="w")
        name.pack(side="left", fill="x", expand=True)
        name.bind("<Button-1>", self._toggle_handler)

        # Priority badge + reset button (reset only visible when overridden)
        self._build_priority_controls()

        # Remove button (optional blocks only)
        if self.key not in core:
            ctk.CTkButton(
                self.header, text="✕", width=22, height=20,
                fg_color="transparent", text_color=TEXT3,
                hover_color=RED_B, corner_radius=4,
                font=("Segoe UI", 10),
                command=self._remove_handler
            ).pack(side="right", padx=(4, 0))

        # ── Body (collapsed by default) ──────────────────────────────────
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self._build_fields(bdef["fields"])

    def _build_priority_controls(self):
        """Priority badge and a small reset button that appears when overridden."""
        pri = self.priorities.get(self.key, "auto")
        is_ov = pri != "auto"

        # Container so badge and reset sit together
        pri_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        pri_frame.pack(side="right", padx=(4, 0))

        self.pri_btn = ctk.CTkButton(
            pri_frame,
            text=f"pos:{pri}" if is_ov else "auto",
            width=54, height=20,
            fg_color=AMBER_B if is_ov else BG3,
            text_color=AMBER if is_ov else TEXT3,
            hover_color=BG4, corner_radius=10,
            font=("Courier New", 9),
            command=self._cycle_priority
        )
        self.pri_btn.pack(side="left")

        # Reset button — only shown when overridden
        self.reset_btn = ctk.CTkButton(
            pri_frame,
            text="↺", width=22, height=20,
            fg_color="transparent",
            text_color=AMBER,
            hover_color=BG4, corner_radius=4,
            font=("Segoe UI", 12),
            command=self._reset_priority
        )
        if is_ov:
            self.reset_btn.pack(side="left", padx=(2, 0))

    # ── Handler methods ──────────────────────────────────────────────────

    def _toggle_handler(self, event=None):  self.toggle()
    def _remove_handler(self):              self.on_remove(self.key)
    def _move_up(self):                     self.on_move_up(self.key)
    def _move_down(self):                   self.on_move_down(self.key)
    def _on_drag_press(self, event=None):   self.on_drag_start(self.key)
    def _on_drag_release(self, event=None): self.on_drag_end()

    # ── Field builders ───────────────────────────────────────────────────

    def _build_fields(self, fields):
        supports_w = model_supports_weights(self.mode, self.active_model)
        w_label    = weight_syntax_label(self.mode, self.active_model)

        for fid, flabel, ftype in fields:

            if ftype == "range":
                # FIX 1: Range fields get their own container that is
                # only packed if the model supports weights.
                # No outer 'row' is created — label and slider live
                # entirely inside weight_row, so nothing is visible
                # when the whole weight_row is hidden.
                val = float(self.vals.get(self.key, {}).get(fid, 1.0) or 1.0)
                weight_row = ctk.CTkFrame(self.body, fg_color="transparent")
                self._weight_rows.append(weight_row)

                # Label (syntax hint) — only inside weight_row
                self.weight_label = ctk.CTkLabel(
                    weight_row, text=w_label, text_color=TEXT3,
                    font=("Courier New", 10), anchor="w"
                )
                self.weight_label.pack(fill="x", padx=8, pady=(4, 0))

                inner = ctk.CTkFrame(weight_row, fg_color="transparent")
                inner.pack(fill="x", padx=8, pady=(2, 6))

                var = tk.DoubleVar(value=val)
                lbl = ctk.CTkLabel(inner, text=f"{val:.1f}", text_color=TEXT,
                                   font=("Courier New", 10), width=30)
                lbl.pack(side="right")
                slider = ctk.CTkSlider(
                    inner, from_=1.0, to=2.0, number_of_steps=10, variable=var,
                    fg_color=BG4, progress_color=PURPLE, button_color=PURPLE,
                    command=self._make_slider_handler(self.key, fid, lbl)
                )
                slider.pack(side="left", fill="x", expand=True, padx=(0, 6))
                self.field_widgets[(self.key, fid)] = ("range", slider, var, lbl)

                # Only pack the whole weight_row if model supports it
                if supports_w:
                    weight_row.pack(fill="x")
                # If not supported, weight_row is never packed → nothing shown

            else:
                # Text and entry fields always visible
                row = ctk.CTkFrame(self.body, fg_color="transparent")
                row.pack(fill="x", padx=8, pady=(0, 6))

                # FIX 3: Field description label font bumped to 11pt
                ctk.CTkLabel(
                    row, text=flabel, text_color=TEXT3,
                    font=("Segoe UI", 11), anchor="w"
                ).pack(fill="x")

                current = self.vals.get(self.key, {}).get(fid, "")

                if ftype == "text":
                    w = ctk.CTkTextbox(
                        row, height=52, fg_color=BG3, text_color=TEXT,
                        font=FONT_SANS, border_color=BORDER, border_width=1,
                        corner_radius=5
                    )
                    w.pack(fill="x")
                    if current:
                        w.insert("1.0", str(current))
                    w.bind("<KeyRelease>", self._make_text_handler(self.key, fid, w))
                    self.field_widgets[(self.key, fid)] = ("text", w)

                elif ftype == "entry":
                    w = ctk.CTkEntry(
                        row, fg_color=BG3, text_color=TEXT,
                        font=FONT_SANS, border_color=BORDER, border_width=1,
                        corner_radius=5
                    )
                    w.pack(fill="x")
                    if current:
                        w.insert(0, str(current))
                    w.bind("<KeyRelease>", self._make_entry_handler(self.key, fid, w))
                    self.field_widgets[(self.key, fid)] = ("entry", w)

    # ── Weight visibility (called by app.py on model switch) ─────────────

    def refresh_weight_visibility(self, mode: str, model_key: str):
        supports_w = model_supports_weights(mode, model_key)
        w_label    = weight_syntax_label(mode, model_key)

        for weight_row in self._weight_rows:
            if supports_w:
                weight_row.pack(fill="x")
                # Update syntax hint label
                for child in weight_row.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text=w_label)
                        break
            else:
                weight_row.pack_forget()

    # ── Field callbacks ──────────────────────────────────────────────────

    def _make_text_handler(self, k, fid, widget):
        def handler(event=None):
            if k not in self.vals: self.vals[k] = {}
            self.vals[k][fid] = widget.get("1.0", "end").strip()
            self.on_change()
        return handler

    def _make_entry_handler(self, k, fid, widget):
        def handler(event=None):
            if k not in self.vals: self.vals[k] = {}
            self.vals[k][fid] = widget.get().strip()
            self.on_change()
        return handler

    def _make_slider_handler(self, k, fid, lbl):
        def handler(val):
            if k not in self.vals: self.vals[k] = {}
            self.vals[k][fid] = round(float(val), 1)
            lbl.configure(text=f"{float(val):.1f}")
            self.on_change()
        return handler

    # ── Priority controls ────────────────────────────────────────────────

    def _cycle_priority(self):
        cur = self.priorities.get(self.key, "auto")
        if cur == "auto":
            self.priorities[self.key] = "0"
        else:
            n = int(cur) + 1
            self.priorities[self.key] = "auto" if n > 9 else str(n)
        self._refresh_priority_badge()
        self.on_change()

    def _reset_priority(self):
        """Reset priority badge back to auto and hide the reset button."""
        self.priorities[self.key] = "auto"
        self._refresh_priority_badge()
        self.on_change()

    def _refresh_priority_badge(self):
        p = self.priorities.get(self.key, "auto")
        is_ov = p != "auto"
        self.pri_btn.configure(
            text=f"pos:{p}" if is_ov else "auto",
            fg_color=AMBER_B if is_ov else BG3,
            text_color=AMBER if is_ov else TEXT3,
        )
        # FIX 2: Show/hide reset button based on override state
        if is_ov:
            self.reset_btn.pack(side="left", padx=(2, 0))
        else:
            self.reset_btn.pack_forget()

    # ── Drag highlight ───────────────────────────────────────────────────

    def set_drag_highlight(self, state):
        """
        state = 'source'  → orange (being dragged)
        state = 'target'  → purple (drop zone)
        state = False     → default
        """
        if state == "source":
            self.configure(border_color=AMBER, fg_color=AMBER_B)
        elif state == "target":
            self.configure(border_color=PURPLE, fg_color=PURPLE_B)
        else:
            self.configure(border_color=BORDER, fg_color=BG2)

    # ── Expand / collapse ────────────────────────────────────────────────

    def toggle(self):
        self.set_expanded(not self.expanded)

    def set_expanded(self, val: bool):
        self.expanded = val
        if val:
            self.body.pack(fill="x", padx=0, pady=(0, 6))
        else:
            self.body.pack_forget()
