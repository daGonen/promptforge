"""
PromptForge — main.py
Entry point. Just launches the app.
by daGonen
"""

import customtkinter as ctk
from ui.app import PromptForgeApp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = PromptForgeApp()
    app.mainloop()
