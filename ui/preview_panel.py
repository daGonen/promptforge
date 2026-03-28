"""
PromptForge — ui/preview_panel.py
Right panel: token budget bar, assembly order list, prompt output, negative output.

Completely decoupled from block logic — receives data and renders it.
To add prompt history or a diff view, add a new section here.

by daGonen
"""

import customtkinter as ctk
from config import *
from data.modes import MODES
from core.assembler import get_order_issues


class PreviewPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG2, corner_radius=0, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=BG2, corner_radius=0, height=42)
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text="ASSEMBLY PREVIEW", text_color=TEXT3,
                     font=("Courier New", 10)).pack(side="left", padx=12, pady=12)
        self.model_lbl = ctk.CTkLabel(hdr, text="", text_color=TEXT3,
                                       font=("Courier New", 9))
        self.model_lbl.pack(side="right", padx=12)

        # Scrollable body
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG2,
            scrollbar_button_color=BG3,
            scrollbar_button_hover_color=BG4,
            corner_radius=0
        )
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.columnconfigure(0, weight=1)

        self._build_token_section()
        self._build_order_section()
        self._build_output_section()
        self._build_negative_section()

    # ── Section helpers ──────────────────────────────────────────────────

    def _section(self, title: str) -> ctk.CTkFrame:
        f = ctk.CTkFrame(self.scroll, fg_color=BG3, corner_radius=8,
                         border_width=1, border_color=BORDER)
        f.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(f, text=title, text_color=TEXT3,
                     font=("Courier New", 9)).pack(anchor="w", padx=10, pady=(8, 4))
        return f

    def _copy_btn(self, parent, label: str, command) -> ctk.CTkButton:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=(0, 8))
        btn = ctk.CTkButton(
            row, text=label, height=28,
            fg_color="transparent", text_color=TEXT2,
            border_width=1, border_color=BORDER,
            hover_color=BG4, corner_radius=6,
            font=FONT_SANS_SM, command=command
        )
        btn.pack(fill="x")
        return btn

    # ── Section builders ─────────────────────────────────────────────────

    def _build_token_section(self):
        f = self._section("TOKEN BUDGET")
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=(0, 4))
        inner.columnconfigure(0, weight=1)

        self.token_bar = ctk.CTkProgressBar(
            inner, height=4, fg_color=BG4, progress_color=TEAL, corner_radius=2
        )
        self.token_bar.set(0)
        self.token_bar.grid(row=0, column=0, sticky="ew", pady=(2, 4))

        self.token_count_lbl = ctk.CTkLabel(
            inner, text="0 / 75", text_color=TEXT2,
            font=("Courier New", 10)
        )
        self.token_count_lbl.grid(row=0, column=1, padx=(8, 0))

        self.token_note_lbl = ctk.CTkLabel(
            f, text="", text_color=TEXT3, font=("Courier New", 9)
        )
        self.token_note_lbl.pack(anchor="w", padx=10, pady=(0, 8))

    def _build_order_section(self):
        f = self._section("ASSEMBLY ORDER")
        self.order_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.order_frame.pack(fill="x", padx=8, pady=(0, 8))

    def _build_output_section(self):
        f = self._section("PROMPT OUTPUT")
        self.output_box = ctk.CTkTextbox(
            f, height=100, fg_color=BG4, text_color=TEXT,
            font=("Courier New", 10), border_width=0, corner_radius=5,
            state="disabled"
        )
        self.output_box.pack(fill="x", padx=8, pady=(0, 6))
        self.copy_btn = self._copy_btn(f, "copy prompt", self._copy_prompt)

    def _build_negative_section(self):
        f = self._section("NEGATIVE PROMPT")
        self.neg_box = ctk.CTkTextbox(
            f, height=55, fg_color=BG4, text_color=RED,
            font=("Courier New", 10), border_width=0, corner_radius=5,
            state="disabled"
        )
        self.neg_box.pack(fill="x", padx=8, pady=(0, 6))
        self.copy_neg_btn = self._copy_btn(f, "copy negative", self._copy_negative)

    # ── Public update method ─────────────────────────────────────────────

    def update(self, mode: str, model_key: str, ordered: list, priorities: dict,
               budget_info: dict, prompt: str, negative: str):
        """
        Called by app.py whenever state changes.
        Receives pre-computed data — no business logic here.
        """
        bd = MODES[mode]["blocks"]
        self.model_lbl.configure(text=budget_info["label"])
        self._prompt = prompt
        self._negative = negative

        # Token bar
        status_color = {
            "ok": TEAL, "warning": AMBER, "over": RED
        }[budget_info["status"]]
        self.token_bar.configure(progress_color=status_color)
        self.token_bar.set(budget_info["pct"])
        self.token_count_lbl.configure(
            text=f"{budget_info['tokens']} / {budget_info['budget']}"
        )
        self.token_note_lbl.configure(
            text=f"optimal: {budget_info['optimal']} tokens · {budget_info['label']}"
        )

        # Assembly order
        for w in self.order_frame.winfo_children():
            w.destroy()

        # Get issues for specific position feedback
        from core.assembler import get_order_issues
        issues      = get_order_issues(mode, model_key, ordered, priorities)
        issue_map   = {i["key"]: i for i in issues}

        for i, k in enumerate(ordered):
            bdef = bd.get(k)
            if not bdef:
                continue
            row = ctk.CTkFrame(self.order_frame, fg_color="transparent", height=24)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=str(i + 1), text_color=TEXT3,
                         font=("Courier New", 9), width=18).pack(side="left")
            ctk.CTkLabel(row, text=f"{bdef['icon']} {bdef['name']}", text_color=TEXT,
                         font=FONT_SANS_SM, anchor="w").pack(side="left", fill="x", expand=True)

            p = priorities.get(k, "auto")
            is_ov = p != "auto"

            if is_ov:
                badge_text  = "override"
                badge_color = AMBER
                badge_bg    = AMBER_B
            elif k in issue_map:
                issue       = issue_map[k]
                # Show: current pos → recommended pos (1-based for readability)
                badge_text  = f"{issue['current']+1}→{issue['preferred']+1}"
                badge_color = AMBER
                badge_bg    = AMBER_B
            else:
                badge_text  = "✓"
                badge_color = TEAL
                badge_bg    = TEAL_B

            ctk.CTkLabel(
                row, text=badge_text, text_color=badge_color,
                fg_color=badge_bg, font=("Courier New", 8),
                corner_radius=6, padx=5, pady=1
            ).pack(side="right")

        # Prompt output
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", prompt if prompt else "fill blocks to generate...")
        self.output_box.configure(state="disabled")

        # Negative
        self.neg_box.configure(state="normal")
        self.neg_box.delete("1.0", "end")
        self.neg_box.insert("1.0", negative if negative else "add negative block...")
        self.neg_box.configure(state="disabled")

    # ── Copy actions ─────────────────────────────────────────────────────

    def _copy_prompt(self):
        import pyperclip
        if hasattr(self, "_prompt") and self._prompt:
            pyperclip.copy(self._prompt)
            self._flash(self.copy_btn, "copied!", "copy prompt")

    def _copy_negative(self):
        import pyperclip
        if hasattr(self, "_negative") and self._negative:
            pyperclip.copy(self._negative)
            self._flash(self.copy_neg_btn, "copied!", "copy negative")

    def _flash(self, btn, flash_text: str, restore_text: str):
        btn.configure(text=flash_text, text_color=TEAL, border_color=TEAL)
        btn.after(1500, lambda: btn.configure(
            text=restore_text, text_color=TEXT2, border_color=BORDER
        ))
