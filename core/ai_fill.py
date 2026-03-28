"""
PromptForge — core/ai_fill.py
AI-assisted block filling via the Anthropic API.

When implemented, this module takes a plain-language description from the user
and returns a structured dict of block values ready to populate the UI.

Status: placeholder — not yet wired to the UI.
by daGonen
"""

# ── To enable AI fill ──────────────────────────────────────────────────────
# 1. pip install anthropic
# 2. Set ANTHROPIC_API_KEY in your environment or a .env file
# 3. Uncomment the code below
# 4. In ui/app.py, add an "AI fill" button that calls fill_blocks_from_description()
# ──────────────────────────────────────────────────────────────────────────

# import os
# import json
# import anthropic
# from data.modes import MODES
#
#
# def fill_blocks_from_description(description: str, mode: str, model_key: str) -> dict:
#     """
#     Send a plain-language description to Claude and get back structured block values.
#
#     Args:
#         description: User's plain text, e.g. "moody portrait of a woman in a rainy Tokyo apartment"
#         mode: Current modality tab, e.g. "image"
#         model_key: Target model, e.g. "flux"
#
#     Returns:
#         Dict of {block_key: {"v": str}} ready to merge into app.vals
#     """
#     blocks = MODES[mode]["blocks"]
#     model_label = MODES[mode]["models"][model_key]["label"]
#
#     block_list = "\n".join(
#         f'- "{k}": {v["name"]} ({v["fields"][0][1]})'
#         for k, v in blocks.items()
#         if k != "negative"
#     )
#
#     system_prompt = f"""You are an expert AI prompt engineer specializing in {model_label}.
# Given a plain-language description, extract structured prompt components and return ONLY valid JSON.
# No preamble, no markdown, no explanation — raw JSON only.
# Optimize each value for {model_label} specifically."""
#
#     user_prompt = f"""Description: "{description}"
#
# Extract values for these prompt blocks:
# {block_list}
#
# Return JSON with this exact shape:
# {{
#   "subject": "...",
#   "style": "...",
#   "mood": "...",
#   ...
# }}
# Only include blocks where you have a confident value. Omit the rest."""
#
#     client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
#     message = client.messages.create(
#         model="claude-sonnet-4-20250514",
#         max_tokens=512,
#         system=system_prompt,
#         messages=[{"role": "user", "content": user_prompt}]
#     )
#
#     raw = message.content[0].text.strip()
#     parsed = json.loads(raw)
#
#     return {k: {"v": v} for k, v in parsed.items() if k in blocks}


def fill_blocks_from_description(description: str, mode: str, model_key: str) -> dict:
    """Placeholder — returns empty dict until API is configured."""
    print("[ai_fill] Not yet configured. See core/ai_fill.py to enable.")
    return {}
