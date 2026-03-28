"""
PromptForge — config.py
App-wide constants, theme colors, and font definitions.
by daGonen
"""

APP_NAME    = "PromptForge"
APP_VERSION = "0.1.0"
APP_AUTHOR  = "daGonen"
APP_TAGLINE = "AI prompt builder · by daGonen"

# ── Colors ─────────────────────────────────────────────────────────────────
BG       = "#0f0f0f"
BG2      = "#161616"
BG3      = "#1e1e1e"
BG4      = "#252525"
BORDER   = "#2a2a2a"
TEXT     = "#e8e8e8"
TEXT2    = "#999999"
TEXT3    = "#666666"

PURPLE   = "#7c6ff7"
PURPLE_B = "#2a2750"
TEAL     = "#2dd4a0"
TEAL_B   = "#0d3326"
AMBER    = "#f0a43a"
AMBER_B  = "#3a2810"
RED      = "#f06060"
RED_B    = "#3a1010"
GREEN    = "#4cbb87"
PINK     = "#e87ea1"
BLUE     = "#5ba4f5"

# ── Fonts ──────────────────────────────────────────────────────────────────
# Bumped up from previous sizes for readability
FONT_MONO    = ("Courier New", 11)   # was 10
FONT_MONO_SM = ("Courier New", 10)   # was 9
FONT_SANS    = ("Segoe UI", 13)      # was 11  — field inputs
FONT_SANS_SM = ("Segoe UI", 12)      # was 10  — block names, pills, chips
FONT_SANS_XS = ("Segoe UI", 11)      # was 9   — small labels, buttons
FONT_BOLD    = ("Segoe UI", 13, "bold")  # was 11

# ── Window ─────────────────────────────────────────────────────────────────
WINDOW_SIZE  = "1200x760"   # slightly wider to accommodate larger text
WINDOW_MIN   = (960, 620)
