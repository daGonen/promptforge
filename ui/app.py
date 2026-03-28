"""
PromptForge — ui/app.py
Main application window. Coordinates all panels and owns app state.

Fixes in this version:
- Default model is now first key in the mode's models dict (Nano Banana for image)
- Drag throttled with _drag_pending flag to reduce jank
- Preview panel update is always called after repack — assembly order now
  reflects drag changes immediately in the right column
- Up/Down arrow callbacks wired to BlockWidget
- Source block gets orange highlight during drag

by daGonen
"""

import customtkinter as ctk
from config import *
from data.modes import MODES
from data.presets import load_presets
from core.assembler import get_assembly_order, get_default_order, build_prompt, token_budget_status, model_supports_weights, get_order_issues
from ui.block_widget import BlockWidget
from ui.preview_panel import PreviewPanel
from ui.preset_bar import PresetBar


class PromptForgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  ·  {APP_TAGLINE}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN)
        self.configure(fg_color=BG)

        # ── App state ────────────────────────────────────────────────────
        self.mode          = "image"
        # Always pick first model from the mode — so Nano Banana is default for image
        self.active_model  = list(MODES["image"]["models"].keys())[0]
        _core = list(MODES["image"]["core"])
        self.active_blocks = get_default_order("image", self.active_model, _core)
        self.vals          = {}
        self.priorities    = {}
        self.presets       = load_presets()
        self.block_widgets = {}
        self.drag_source   = None
        self.drag_target   = None
        self.drawer_open   = False
        # Throttle flag — prevents reorder firing on every pixel of mouse movement
        self._drag_pending = False

        self._init_vals()
        self._build_layout()
        self._render_blocks()
        self._update_preview()

        # Root-level mouse tracking for drag
        self.bind("<B1-Motion>",       self._on_drag_motion)
        self.bind("<ButtonRelease-1>", self._on_drag_release)

    # ── State helpers ────────────────────────────────────────────────────

    def _init_vals(self):
        for k, bdef in MODES[self.mode]["blocks"].items():
            self.vals.setdefault(k, {})
            self.priorities.setdefault(k, "auto")
            for fid, _, ftype in bdef["fields"]:
                self.vals[k].setdefault(fid, 1.0 if ftype == "range" else "")

    def _get_state(self) -> dict:
        return {
            "mode":       self.mode,
            "model":      self.active_model,
            "blocks":     list(self.active_blocks),
            "vals":       self.vals,
            "priorities": self.priorities,
        }

    def _set_state(self, preset: dict):
        self.active_model  = preset["model"]
        self.active_blocks = list(preset["blocks"])
        self.vals          = {}
        self.priorities    = {}
        for k, v in preset.get("vals", {}).items():
            self.vals[k] = dict(v)
        for k, v in preset.get("priorities", {}).items():
            self.priorities[k] = v
        self._init_vals()
        self._render_model_pills()
        self._render_blocks()
        self._update_preview()

    # ── Layout ───────────────────────────────────────────────────────────

    def _build_layout(self):
        main = ctk.CTkFrame(self, fg_color=BG)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self.left = ctk.CTkFrame(main, fg_color=BG, corner_radius=0)
        self.left.grid(row=0, column=0, sticky="nsew")
        self.left.columnconfigure(0, weight=1)
        self.left.rowconfigure(4, weight=1)

        ctk.CTkFrame(main, fg_color=BORDER, width=1).grid(row=0, column=0, sticky="nse")

        self.preview = PreviewPanel(main)
        self.preview.grid(row=0, column=1, sticky="nsew")

        self._build_topbar()
        self._build_preset_bar()
        self._build_model_row()
        self._build_order_warn_bar()
        self._build_blocks_area()
        self._build_add_row()

    def _build_topbar(self):
        bar = ctk.CTkFrame(self.left, fg_color=BG2, corner_radius=0, height=46)
        bar.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            bar, text=f"⬡  {APP_NAME}", text_color=PURPLE,
            font=("Courier New", 14, "bold")
        ).pack(side="left", padx=(14, 10), pady=10)

        ctk.CTkFrame(bar, fg_color=BORDER, width=1, height=20).pack(
            side="left", pady=12, padx=4)

        self.tab_btns = {}
        for m in ["image", "video", "language", "audio"]:
            b = ctk.CTkButton(
                bar, text=m, width=70, height=28,
                fg_color=PURPLE_B if m == self.mode else "transparent",
                text_color=PURPLE if m == self.mode else TEXT3,
                hover_color=BG3, corner_radius=6,
                font=FONT_SANS_XS,
                command=lambda x=m: self._switch_mode(x)
            )
            b.pack(side="left", padx=2, pady=9)
            self.tab_btns[m] = b

        ctk.CTkLabel(
            bar, text=f"v{APP_VERSION}  ·  {APP_AUTHOR}",
            text_color=TEXT3, font=FONT_MONO_SM
        ).pack(side="right", padx=14)

    def _build_preset_bar(self):
        self.preset_bar = PresetBar(
            self.left,
            get_state=self._get_state,
            set_state=self._set_state,
            get_mode=lambda: self.mode,
        )
        self.preset_bar.grid(row=1, column=0, sticky="ew")
        self.preset_bar.load(self.presets, self.mode)

    def _build_model_row(self):
        self.model_row_frame = ctk.CTkFrame(
            self.left, fg_color=BG, corner_radius=0, height=40)
        self.model_row_frame.grid(row=2, column=0, sticky="ew")
        self._render_model_pills()

    def _render_model_pills(self):
        for w in self.model_row_frame.winfo_children():
            w.destroy()
        for k, mdata in MODES[self.mode]["models"].items():
            is_active = k == self.active_model
            ctk.CTkButton(
                self.model_row_frame, text=mdata["label"], width=-1, height=26,
                fg_color=TEAL_B if is_active else "transparent",
                text_color=TEAL if is_active else TEXT2,
                border_width=1, border_color=BORDER,
                hover_color=BG3, corner_radius=20,
                font=FONT_SANS_SM,
                command=lambda x=k: self._set_model(x)
            ).pack(side="left", padx=(6, 2), pady=7)


    def _build_order_warn_bar(self):
        """
        Order warning bar — sits between model row and blocks scroll.
        Hidden when order matches model recommendations.
        Shows recommended vs current order with a reset button when different.
        """
        self.order_warn_frame = ctk.CTkFrame(
            self.left, fg_color=AMBER_B, corner_radius=0
        )
        # grid row=3, only shown when needed
        self._order_warn_visible = False

    def _refresh_order_warning(self):
        """
        Recompute order issues and update the warning bar.
        Called from _update_preview() every time state changes.
        """
        issues = get_order_issues(
            self.mode, self.active_model, self.active_blocks, self.priorities
        )

        if not issues:
            # Hide bar if showing
            if self._order_warn_visible:
                self.order_warn_frame.grid_forget()
                self._order_warn_visible = False
            return

        # Show bar
        if not self._order_warn_visible:
            self.order_warn_frame.grid(row=3, column=0, sticky="ew")
            self._order_warn_visible = True

        # Rebuild contents
        for w in self.order_warn_frame.winfo_children():
            w.destroy()

        bd          = MODES[self.mode]["blocks"]
        model_order = MODES[self.mode]["models"][self.active_model]["order"]
        model_label = MODES[self.mode]["models"][self.active_model]["label"]

        # Preferred order among active blocks only
        preferred = [k for k in model_order if k in self.active_blocks]
        extras    = [k for k in self.active_blocks if k not in model_order]
        preferred = preferred + extras

        # Header row
        hdr = ctk.CTkFrame(self.order_warn_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=(7, 3))

        ctk.CTkLabel(
            hdr,
            text=f"⚠  order differs from {model_label} recommendation",
            text_color=AMBER, font=("Segoe UI", 11, "bold"), anchor="w"
        ).pack(side="left")

        ctk.CTkButton(
            hdr, text="↺ reset order", height=22, width=100,
            fg_color="transparent", text_color=AMBER,
            border_width=1, border_color=AMBER,
            hover_color=BG3, corner_radius=5,
            font=("Segoe UI", 10),
            command=self._reset_to_model_order
        ).pack(side="right")

        # Recommended row
        rec_row = ctk.CTkFrame(self.order_warn_frame, fg_color="transparent")
        rec_row.pack(fill="x", padx=10, pady=(0, 2))
        ctk.CTkLabel(
            rec_row, text="recommended:", text_color=TEXT3,
            font=("Courier New", 9), width=90, anchor="w"
        ).pack(side="left")

        # Build recommended arrows — highlight misplaced blocks in amber
        issue_keys = {i["key"] for i in issues}
        rec_parts  = []
        for k in preferred:
            name  = bd[k]["name"] if k in bd else k
            color = AMBER if k in issue_keys else TEXT2
            rec_parts.append((name, color))

        for idx, (name, color) in enumerate(rec_parts):
            ctk.CTkLabel(
                rec_row, text=name, text_color=color,
                font=("Segoe UI", 10)
            ).pack(side="left")
            if idx < len(rec_parts) - 1:
                ctk.CTkLabel(
                    rec_row, text=" → ", text_color=TEXT3,
                    font=("Segoe UI", 10)
                ).pack(side="left")

        # Current row
        cur_row = ctk.CTkFrame(self.order_warn_frame, fg_color="transparent")
        cur_row.pack(fill="x", padx=10, pady=(0, 7))
        ctk.CTkLabel(
            cur_row, text="your order:", text_color=TEXT3,
            font=("Courier New", 9), width=90, anchor="w"
        ).pack(side="left")

        cur_parts = []
        for k in self.active_blocks:
            name  = bd[k]["name"] if k in bd else k
            color = AMBER if k in issue_keys else TEXT2
            cur_parts.append((name, color))

        for idx, (name, color) in enumerate(cur_parts):
            ctk.CTkLabel(
                cur_row, text=name, text_color=color,
                font=("Segoe UI", 10)
            ).pack(side="left")
            if idx < len(cur_parts) - 1:
                ctk.CTkLabel(
                    cur_row, text=" → ", text_color=TEXT3,
                    font=("Segoe UI", 10)
                ).pack(side="left")

    def _reset_to_model_order(self):
        """Reset active_blocks to model-preferred order, keep values intact."""
        self.active_blocks = get_default_order(
            self.mode, self.active_model, self.active_blocks
        )
        self._render_blocks()
        self._update_preview()

    def _build_blocks_area(self):
        self.blocks_scroll = ctk.CTkScrollableFrame(
            self.left, fg_color=BG,
            scrollbar_button_color=BG3,
            scrollbar_button_hover_color=BG4,
            corner_radius=0
        )
        self.blocks_scroll.grid(row=4, column=0, sticky="nsew")
        self.blocks_scroll.columnconfigure(0, weight=1)

    def _build_add_row(self):
        add_row = ctk.CTkFrame(self.left, fg_color=BG2, corner_radius=0, height=46)
        add_row.grid(row=5, column=0, sticky="ew")

        ctk.CTkButton(
            add_row, text="+ add block", height=30,
            fg_color="transparent", text_color=TEXT3,
            border_width=1, border_color=BORDER,
            hover_color=BG3, corner_radius=6,
            font=FONT_SANS_SM,
            command=self._toggle_drawer
        ).pack(fill="x", padx=10, pady=8)

        self.drawer_frame = ctk.CTkFrame(self.left, fg_color=BG3, corner_radius=0)

    def _toggle_drawer(self):
        self.drawer_open = not self.drawer_open
        if self.drawer_open:
            self.drawer_frame.grid(row=6, column=0, sticky="ew")
            self._render_drawer()
        else:
            self.drawer_frame.grid_forget()

    def _render_drawer(self):
        for w in self.drawer_frame.winfo_children():
            w.destroy()
        bd   = MODES[self.mode]["blocks"]
        core = MODES[self.mode]["core"]
        optional = [k for k in bd if k not in core]

        frame = ctk.CTkFrame(self.drawer_frame, fg_color="transparent")
        frame.pack(fill="x", padx=8, pady=8)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        for col, k in enumerate(optional):
            used = k in self.active_blocks
            ctk.CTkButton(
                frame,
                text=f"{bd[k]['icon']} {bd[k]['name']}" + (" ✓" if used else ""),
                width=160, height=28,
                fg_color="transparent",
                text_color=TEXT3 if used else TEXT2,
                border_width=1, border_color=BORDER,
                hover_color=BG4, corner_radius=5,
                font=FONT_SANS_SM,
                state="disabled" if used else "normal",
                command=lambda x=k: self._add_block(x)
            ).grid(row=col // 2, column=col % 2, padx=3, pady=2, sticky="ew")

    # ── Block management ─────────────────────────────────────────────────

    def _render_blocks(self):
        """Full rebuild — only called on mode/preset switch or add/remove."""
        for w in self.blocks_scroll.winfo_children():
            w.destroy()
        self.block_widgets = {}

        for key in self.active_blocks:
            if key not in MODES[self.mode]["blocks"]:
                continue
            bw = BlockWidget(
                self.blocks_scroll,
                key=key,
                mode=self.mode,
                vals=self.vals,
                priorities=self.priorities,
                on_change=self._update_preview,
                on_remove=self._remove_block,
                on_drag_start=self._drag_start,
                on_drag_end=self._drag_end,
                on_move_up=self._move_block_up,
                on_move_down=self._move_block_down,
                active_blocks=self.active_blocks,
                active_model=self.active_model,
            )
            bw.pack(fill="x", padx=8, pady=(0, 5))
            self.block_widgets[key] = bw

    def _repack_blocks(self):
        """
        Lightweight reorder — no widget destruction.
        Unpacks and repacks existing widgets in new order.
        Always call _update_preview() after this.
        """
        for bw in self.block_widgets.values():
            bw.pack_forget()
        for key in self.active_blocks:
            if key in self.block_widgets:
                self.block_widgets[key].pack(fill="x", padx=8, pady=(0, 5))

    def _add_block(self, key: str):
        if key not in self.active_blocks:
            self.active_blocks.append(key)
            self._init_vals()
            self._render_blocks()
            self._render_drawer()
            self._update_preview()

    def _remove_block(self, key: str):
        if key in self.active_blocks:
            self.active_blocks.remove(key)
            self._render_blocks()
            if self.drawer_open:
                self._render_drawer()
            self._update_preview()

    # ── Up / Down arrow reorder (reliable fallback) ──────────────────────

    def _move_block_up(self, key: str):
        i = self.active_blocks.index(key)
        if i > 0:
            self.active_blocks[i], self.active_blocks[i - 1] = \
                self.active_blocks[i - 1], self.active_blocks[i]
            self._repack_blocks()
            self._update_preview()

    def _move_block_down(self, key: str):
        i = self.active_blocks.index(key)
        if i < len(self.active_blocks) - 1:
            self.active_blocks[i], self.active_blocks[i + 1] = \
                self.active_blocks[i + 1], self.active_blocks[i]
            self._repack_blocks()
            self._update_preview()

    def _drag_start(self, key: str):
        self.drag_source = key
        self.drag_target = None
        self._drag_pending = False
        # Orange highlight on the block being dragged
        if key in self.block_widgets:
            self.block_widgets[key].set_drag_highlight("source")

    def _drag_end(self):
        # Clear all highlights
        for bw in self.block_widgets.values():
            bw.set_drag_highlight(False)
        self.drag_source   = None
        self.drag_target   = None
        self._drag_pending = False

    def _on_drag_motion(self, event):
        if not self.drag_source:
            return
        # Throttle: skip if we already have a pending update
        if self._drag_pending:
            return
        self._drag_pending = True
        # Schedule the actual reorder logic on the next event loop tick
        self.after(16, lambda: self._process_drag(event.x_root, event.y_root))

    def _process_drag(self, x_root, y_root):
        """Actual drag logic — runs at most ~60fps via after(16)."""
        self._drag_pending = False

        if not self.drag_source:
            return

        widget_under = self.winfo_containing(x_root, y_root)
        target_key   = self._find_block_key_for_widget(widget_under)

        # Not over a valid target
        if target_key is None or target_key == self.drag_source:
            # Keep source orange, clear everything else
            for k, bw in self.block_widgets.items():
                bw.set_drag_highlight("source" if k == self.drag_source else False)
            self.drag_target = None
            return

        # Update highlights
        for k, bw in self.block_widgets.items():
            if k == self.drag_source:
                bw.set_drag_highlight("source")
            elif k == target_key:
                bw.set_drag_highlight("target")
            else:
                bw.set_drag_highlight(False)

        # Only reorder if target actually changed
        if target_key == self.drag_target:
            return

        self.drag_target = target_key
        si = self.active_blocks.index(self.drag_source)
        ti = self.active_blocks.index(target_key)

        if si != ti:
            self.active_blocks.remove(self.drag_source)
            ti = self.active_blocks.index(target_key)
            self.active_blocks.insert(ti, self.drag_source)

            self._repack_blocks()

            # Restore highlights after repack (widgets still exist, just repacked)
            for k, bw in self.block_widgets.items():
                if k == self.drag_source:
                    bw.set_drag_highlight("source")
                elif k == target_key:
                    bw.set_drag_highlight("target")
                else:
                    bw.set_drag_highlight(False)

            # Always update preview so right column reflects new order
            self._update_preview()

    def _on_drag_release(self, event):
        if self.drag_source:
            self._drag_end()

    def _find_block_key_for_widget(self, widget) -> str | None:
        """Walk up widget tree to find owning BlockWidget, return its key."""
        w = widget
        while w is not None:
            if isinstance(w, BlockWidget):
                return w.key
            try:
                w = w.master
            except AttributeError:
                break
        return None

    # ── Mode / model switching ───────────────────────────────────────────

    def _switch_mode(self, m: str):
        self.mode          = m
        # Always pick first model in the dict — order in modes.py controls default
        self.active_model  = list(MODES[m]["models"].keys())[0]
        _core = list(MODES[m]["core"])
        self.active_blocks = get_default_order(m, self.active_model, _core)
        self.vals          = {}
        self.priorities    = {}
        self.drag_source   = None
        self.drag_target   = None
        self._drag_pending = False
        self._init_vals()

        for tab, btn in self.tab_btns.items():
            btn.configure(
                fg_color=PURPLE_B if tab == m else "transparent",
                text_color=PURPLE if tab == m else TEXT3,
            )

        self._render_model_pills()
        self.preset_bar.load(self.presets, m, active_preset=None)
        self._render_blocks()
        self._update_preview()

        if self.drawer_open:
            self._toggle_drawer()

    def _set_model(self, key: str):
        self.active_model = key
        self._render_model_pills()
        # Update weight slider visibility for all active blocks
        for bw in self.block_widgets.values():
            bw.refresh_weight_visibility(self.mode, key)
        self._update_preview()

    # ── Preview update ───────────────────────────────────────────────────

    def _update_preview(self):
        """
        Always recomputes from scratch using current active_blocks order.
        This is the single source of truth for the right panel.
        """
        ordered = get_assembly_order(
            self.mode, self.active_model, self.active_blocks, self.priorities
        )
        prompt, negative = build_prompt(
            self.mode, self.active_model, self.active_blocks, self.priorities, self.vals
        )
        budget = token_budget_status(self.mode, self.active_model, prompt)

        self.preview.update(
            mode=self.mode,
            model_key=self.active_model,
            ordered=ordered,
            priorities=self.priorities,
            budget_info=budget,
            prompt=prompt,
            negative=negative,
        )
        self._refresh_order_warning()
