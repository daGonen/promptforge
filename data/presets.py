"""
PromptForge — data/presets.py
Default preset definitions and disk persistence (presets.json).
by daGonen
"""

import json
import os

PRESETS_FILE = os.path.join(os.path.dirname(__file__), "..", "user_data", "presets.json")

DEFAULT_PRESETS = {
    "image": [
        {
            "name": "nb portrait",
            "model": "nano",
            "blocks": ["subject", "action", "scene", "style", "camera", "lighting"],
            "vals": {
                "subject": {"v": "a woman in her early 30s, soft expression, dark hair loosely tucked behind one ear"},
                "action":  {"v": "standing still, looking slightly off camera, holding a ceramic mug with both hands"},
                "scene":   {"v": "rainy Tokyo apartment interior, early morning, condensation on the window behind her"},
                "style":   {"v": "analog film photography, 35mm, realistic, not stylized"},
                "camera":  {"v": "medium close-up, f/1.8 shallow depth of field, subject placement slightly left of center"},
                "lighting":{"v": "soft diffused window light, overcast sky, cool natural tones, no harsh shadows"},
            },
            "priorities": {}
        },
        {
            "name": "nb product",
            "model": "nano",
            "blocks": ["subject", "action", "scene", "style", "lighting", "color", "technical"],
            "vals": {
                "subject":   {"v": "a small glass jar of loose-leaf wellness tea, label facing forward"},
                "action":    {"v": "sitting on a minimal surface, nothing else in frame competing with it"},
                "scene":     {"v": "clean white surface, soft out-of-focus background, indoor studio"},
                "style":     {"v": "commercial product photography, crisp and clean, high-end brand aesthetic"},
                "lighting":  {"v": "soft studio lighting, no harsh shadows, slight rim light on the jar"},
                "color":     {"v": "warm earth tones, muted greens, natural palette"},
                "technical": {"v": "sharp focus throughout, no grain, no watermarks, high resolution"},
            },
            "priorities": {}
        },
        {
            "name": "flux portrait",
            "model": "flux",
            "blocks": ["subject", "style", "lighting", "mood", "camera"],
            "vals": {
                "subject":  {"v": "close-up portrait of a woman, soft expression"},
                "style":    {"v": "analog film photography, 35mm grain"},
                "lighting": {"v": "soft diffused window light, overcast"},
                "mood":     {"v": "calm, introspective, quiet"},
                "camera":   {"v": "f/1.8 shallow depth of field"},
            },
            "priorities": {}
        },
        {
            "name": "flux product",
            "model": "flux",
            "blocks": ["subject", "style", "lighting", "color", "technical"],
            "vals": {
                "subject":   {"v": "tea product on minimal white surface"},
                "style":     {"v": "commercial product photography, clean"},
                "lighting":  {"v": "soft studio lighting, no harsh shadows"},
                "color":     {"v": "warm earth tones, muted greens"},
                "technical": {"v": "4k, sharp focus, no grain"},
            },
            "priorities": {}
        },
    ],
    "video": [
        {
            "name": "veo3 dialogue",
            "model": "veo3",
            "blocks": ["subject", "scene", "motion", "camera", "style", "mood", "audio"],
            "vals": {
                "subject": {"v": "a woman in her 30s, warm expression, casual clothing"},
                "scene":   {"v": "bright minimal interior, soft neutral background, morning light"},
                "motion":  {"v": "slight natural head movement, relaxed body language, speaking to camera"},
                "camera":  {"v": "medium shot, static, slight breathing motion, eye-level"},
                "style":   {"v": "clean cinematic, natural color grade, no heavy processing"},
                "mood":    {"v": "warm, approachable, conversational"},
                "audio":   {"v": "clear natural voice, ambient room tone, no music"},
            },
            "priorities": {}
        },
        {
            "name": "veo3 cinematic",
            "model": "veo31",
            "blocks": ["subject", "scene", "motion", "camera", "style", "mood", "lighting", "audio"],
            "vals": {
                "subject":  {"v": "a lone figure walking across a frost-covered bridge at dawn"},
                "scene":    {"v": "pale morning light, soft curling fog clinging to bridge railings, bare trees fading into mist"},
                "motion":   {"v": "slow unhurried walk, coat moving slightly in the breeze"},
                "camera":   {"v": "wide eye-level shot, slow dolly following the subject from behind"},
                "style":    {"v": "cinematic naturalistic, anamorphic widescreen, slight film grain"},
                "mood":     {"v": "quiet, reflective, melancholic but not heavy"},
                "lighting": {"v": "soft diffused dawn light, cool blue-grey tones, no direct sun"},
                "audio":    {"v": "quiet footsteps on frost, distant birdsong, low ambient wind"},
            },
            "priorities": {}
        },
        {
            "name": "talking head",
            "model": "wan22",
            "blocks": ["subject", "motion", "scene", "camera"],
            "vals": {
                "subject": {"v": "woman looking at camera, speaking naturally"},
                "motion":  {"v": "subtle head movement, lips moving, slight breathing"},
                "scene":   {"v": "minimal bright interior, soft background"},
                "camera":  {"v": "static shot, slight breathing motion"},
            },
            "priorities": {}
        },
    ],
    "language": [
        {
            "name": "brand copy",
            "model": "claude",
            "blocks": ["role", "task", "tone", "constraints"],
            "vals": {
                "role":        {"v": "expert wellness brand copywriter"},
                "task":        {"v": "write short product description for wellness tea"},
                "tone":        {"v": "warm, direct, friend-to-friend energy, not clinical"},
                "constraints": {"v": "max 60 words, no wellness clichés"},
            },
            "priorities": {}
        },
    ],
    "audio": [
        {
            "name": "maayan voice",
            "model": "eleven",
            "blocks": ["voice", "emotion", "pace", "style", "context"],
            "vals": {
                "voice":   {"v": "young woman, warm and clear, slight brightness in tone"},
                "emotion": {"v": "upbeat, friendly, genuine, not performative"},
                "pace":    {"v": "natural conversational speed, light pauses between thoughts"},
                "style":   {"v": "friend-to-friend, relatable, not instructional or soft"},
                "context": {"v": "wellness lifestyle influencer promoting yoga and tea products"},
            },
            "priorities": {}
        },
    ]
}


def load_presets() -> dict:
    """Load presets from disk. Falls back to defaults if file doesn't exist or is corrupt."""
    os.makedirs(os.path.dirname(PRESETS_FILE), exist_ok=True)
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {k: list(v) for k, v in DEFAULT_PRESETS.items()}


def save_presets(presets: dict) -> None:
    """Persist presets to disk."""
    os.makedirs(os.path.dirname(PRESETS_FILE), exist_ok=True)
    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2, ensure_ascii=False)
