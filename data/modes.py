"""
PromptForge — data/modes.py
All modality definitions: models, blocks, fields, and assembly orders.

HOW TO ADD A NEW MODEL:
  1. Find the right modality dict (image / video / language / audio)
  2. Add an entry under "models" — key, label, budget, optimal, order
  3. The order list controls assembly sequence — match the model's docs
  4. If the model needs a block that doesn't exist yet, add it to "blocks"
  5. That's it. The UI picks it up automatically.

HOW TO ADD A NEW BLOCK:
  1. Add an entry to "blocks" under the right modality
  2. Add the block key to the "order" list of each model where it fits
  3. If it should always be visible, add it to "core" — else it's optional

by daGonen
"""

MODES = {
    "image": {
        "models": {
            # ── Nano Banana first — Google's conversational image model ──────
            # Source: nanobanana.io/prompt-guide + Google Cloud blog
            # Order: subject → action/relationship → setting → style →
            #        composition/camera → lighting/color → quality → negative
            # Nano Banana uses natural language sentences, not keyword lists.
            # Action/relationship between subject and scene is weighted early.
            # Longer prompts work better here than on diffusion models.
            "nano": {
                "label":   "Nano Banana",
                "budget":  120,
                "optimal": "80–120",
                "weight_syntax": "none",
                "order":   ["subject", "action", "scene", "style", "medium",
                            "camera", "lighting", "color", "technical", "negative"]
            },
            "nanopro": {
                "label":   "Nano Banana Pro",
                "budget":  150,
                "optimal": "100–150",
                "weight_syntax": "none",
                "order":   ["subject", "action", "scene", "style", "medium",
                            "camera", "lighting", "color", "technical", "negative"]
            },
            # ── Diffusion models ─────────────────────────────────────────────
            "flux": {
                "label":   "Flux Dev",
                "budget":  75,
                "optimal": "55–75",
                "weight_syntax": "none",
                "order":   ["subject", "style", "medium", "lighting",
                            "mood", "color", "camera", "technical", "negative"]
            },
            "sdxl": {
                "label":   "SDXL",
                "budget":  77,
                "optimal": "55–77",
                "weight_syntax": "a1111",
                "order":   ["subject", "style", "lighting", "mood",
                            "camera", "color", "medium", "technical", "negative"]
            },
            "mj": {
                "label":   "Midjourney",
                "budget":  60,
                "optimal": "40–60",
                "weight_syntax": "mj",
                "order":   ["subject", "style", "mood", "lighting",
                            "medium", "color", "camera", "technical", "negative"]
            },
            "dalle": {
                "label":   "DALL-E 3",
                "budget":  90,
                "optimal": "60–90",
                "weight_syntax": "none",
                "order":   ["subject", "style", "mood", "lighting",
                            "color", "camera", "medium", "technical", "negative"]
            },
        },
        "core": ["subject", "style", "mood"],
        "blocks": {
            "subject":   {"name": "subject",             "icon": "◎",
                          "fields": [("v", "who or what is in the scene?",       "text"),
                                     ("w", "emphasis weight",                     "range")]},
            # action block — important for Nano Banana, optional for diffusion
            "action":    {"name": "action / relationship","icon": "▶",
                          "fields": [("v", "what is the subject doing? how does it interact with the scene?", "entry")]},
            "style":     {"name": "style",               "icon": "◈",
                          "fields": [("v", "artistic style or aesthetic",         "text"),
                                     ("w", "emphasis weight",                     "range")]},
            "mood":      {"name": "mood",                "icon": "◉",
                          "fields": [("v", "emotion, atmosphere, feeling",        "entry"),
                                     ("w", "emphasis weight",                     "range")]},
            "scene":     {"name": "scene / setting",     "icon": "◱",
                          "fields": [("v", "place, time of day, weather, environment", "entry")]},
            "lighting":  {"name": "lighting",            "icon": "◐",
                          "fields": [("v", "lighting setup or quality",           "entry"),
                                     ("w", "emphasis weight",                     "range")]},
            "camera":    {"name": "camera",              "icon": "◫",
                          "fields": [("v", "lens, angle, framing, depth of field","entry"),
                                     ("w", "emphasis weight",                     "range")]},
            "color":     {"name": "color palette",       "icon": "◑",
                          "fields": [("v", "palette, tones, temperature",         "entry")]},
            "medium":    {"name": "medium",              "icon": "▣",
                          "fields": [("v", "physical medium (oil, film, etc.)",   "entry")]},
            "technical": {"name": "technical",           "icon": "▤",
                          "fields": [("v", "quality tags, resolution",            "entry")]},
            "negative":  {"name": "negative",            "icon": "◻",
                          "fields": [("v", "what to exclude",                     "text")]},
        }
    },

    "video": {
        "models": {
            # ── Veo 3 first — Google's native audio video model ─────────────
            # Source: deepmind.google/models/veo/prompt-guide +
            #         docs.cloud.google.com/vertex-ai + leonardo.ai/news
            # Order: subject → scene/context → action/motion → camera shot →
            #        camera movement → style → mood → lighting → audio → technical
            # Key difference from other video models: Veo 3 generates AUDIO natively.
            # Audio block should be explicit — dialogue, sound effects, ambience.
            # Prompt length: 3–6 sentences (100–150 words) works best per Leonardo guide.
            # Veo responds well to cinematic language: shot types, camera movements.
            "veo3": {
                "label":   "Veo 3",
                "budget":  120,
                "optimal": "80–120",
                "weight_syntax": "none",
                "order":   ["subject", "scene", "motion", "camera", "style",
                            "mood", "lighting", "audio", "technical", "negative"]
            },
            "veo31": {
                "label":   "Veo 3.1",
                "budget":  120,
                "optimal": "80–120",
                "weight_syntax": "none",
                "order":   ["subject", "scene", "motion", "camera", "style",
                            "mood", "lighting", "audio", "technical", "negative"]
            },
            # ── Other video models ───────────────────────────────────────────
            "wan21": {
                "label":   "WAN 2.1",
                "budget":  80,
                "optimal": "60–80",
                "weight_syntax": "none",
                "order":   ["subject", "motion", "scene", "camera", "style",
                            "mood", "duration", "technical", "negative"]
            },
            "wan22": {
                "label":   "WAN 2.2",
                "budget":  80,
                "optimal": "60–80",
                "weight_syntax": "none",
                "order":   ["subject", "motion", "scene", "style", "camera",
                            "mood", "duration", "technical", "negative"]
            },
            "kling": {
                "label":   "Kling",
                "budget":  60,
                "optimal": "40–60",
                "weight_syntax": "none",
                "order":   ["subject", "scene", "motion", "style", "camera",
                            "mood", "technical", "negative"]
            },
            "ltx": {
                "label":   "LTX",
                "budget":  70,
                "optimal": "50–70",
                "weight_syntax": "none",
                "order":   ["subject", "motion", "scene", "style", "mood",
                            "camera", "technical", "negative"]
            },
        },
        "core": ["subject", "motion", "scene"],
        "blocks": {
            "subject":   {"name": "subject",            "icon": "◎",
                          "fields": [("v", "who or what is the main subject?",           "text")]},
            "motion":    {"name": "motion",             "icon": "▷",
                          "fields": [("v", "how does the subject move?",                 "text"),
                                     ("w", "motion intensity",                           "range")]},
            "scene":     {"name": "scene / environment","icon": "◱",
                          "fields": [("v", "location, background, setting, time of day", "text")]},
            "camera":    {"name": "camera movement",    "icon": "◫",
                          "fields": [("v", "shot type (CU/MS/WS) + movement (dolly/pan/static)","entry")]},
            "style":     {"name": "visual style",       "icon": "◈",
                          "fields": [("v", "cinematic look, film stock, render style",   "entry")]},
            "mood":      {"name": "mood",               "icon": "◉",
                          "fields": [("v", "atmosphere, tone, feeling",                  "entry")]},
            "lighting":  {"name": "lighting",           "icon": "◐",
                          "fields": [("v", "lighting quality, direction, color temp",    "entry")]},
            # audio block — native to Veo 3, optional for WAN/Kling
            "audio":     {"name": "audio / dialogue",   "icon": "♪",
                          "fields": [("v", "dialogue, sound effects, ambient audio, music", "text")]},
            "duration":  {"name": "duration / timing",  "icon": "◷",
                          "fields": [("v", "clip length, pacing (e.g. 4s, slow)",        "entry")]},
            "technical": {"name": "technical",          "icon": "▤",
                          "fields": [("v", "resolution, fps, aspect ratio",              "entry")]},
            "negative":  {"name": "negative",           "icon": "◻",
                          "fields": [("v", "what to exclude",                            "text")]},
        }
    },

    "language": {
        "models": {
            "claude":  {"label": "Claude",   "budget": 200, "optimal": "100–200",
                "weight_syntax": "none",
                        "order": ["role","task","context","tone","format","constraints","examples","negative"]},
            "gpt4":    {"label": "GPT-4",    "budget": 200, "optimal": "80–200",
                "weight_syntax": "none",
                        "order": ["role","task","context","tone","format","constraints","examples","negative"]},
            "gemini":  {"label": "Gemini",   "budget": 200, "optimal": "80–200",
                "weight_syntax": "none",
                        "order": ["task","role","context","tone","format","constraints","negative"]},
            "llama":   {"label": "Llama 3",  "budget": 180, "optimal": "80–180",
                "weight_syntax": "none",
                        "order": ["role","task","context","tone","format","constraints","negative"]},
        },
        "core": ["role", "task", "tone"],
        "blocks": {
            "role":        {"name": "role / persona", "icon": "◎",
                            "fields": [("v", "who should the AI act as?",               "text")]},
            "task":        {"name": "task",           "icon": "▣",
                            "fields": [("v", "what do you want it to do?",              "text")]},
            "tone":        {"name": "tone",           "icon": "◉",
                            "fields": [("v", "how should it sound?",                    "entry")]},
            "context":     {"name": "context",        "icon": "◱",
                            "fields": [("v", "background info, audience, situation",    "text")]},
            "format":      {"name": "output format",  "icon": "▤",
                            "fields": [("v", "list, JSON, markdown, paragraph...",      "entry")]},
            "constraints": {"name": "constraints",    "icon": "◫",
                            "fields": [("v", "length limit, rules, what to avoid",      "entry")]},
            "examples":    {"name": "examples",       "icon": "◈",
                            "fields": [("v", "few-shot examples or reference",          "text")]},
            "negative":    {"name": "negative",       "icon": "◻",
                            "fields": [("v", "what to never do or include",             "text")]},
        }
    },

    "audio": {
        "models": {
            "eleven": {"label": "ElevenLabs", "budget": 100, "optimal": "60–100",
                "weight_syntax": "none",
                       "order": ["voice","emotion","pace","style","context","negative"]},
            "suno":   {"label": "Suno",       "budget": 80,  "optimal": "40–80",
                "weight_syntax": "none",
                       "order": ["genre","mood","instruments","tempo","vocals","style","negative"]},
            "udio":   {"label": "Udio",       "budget": 80,  "optimal": "40–80",
                "weight_syntax": "none",
                       "order": ["genre","mood","instruments","tempo","vocals","style","negative"]},
        },
        "core": ["voice", "emotion", "pace"],
        "blocks": {
            "voice":       {"name": "voice character", "icon": "◎",
                            "fields": [("v", "describe voice quality and character",    "text")]},
            "emotion":     {"name": "emotion",         "icon": "◉",
                            "fields": [("v", "emotional tone, feeling, delivery",       "entry")]},
            "pace":        {"name": "pace / rhythm",   "icon": "◷",
                            "fields": [("v", "speaking speed, pauses, cadence",         "entry")]},
            "style":       {"name": "style",           "icon": "◈",
                            "fields": [("v", "conversational, broadcast, whisper...",   "entry")]},
            "context":     {"name": "context",         "icon": "◱",
                            "fields": [("v", "what is this audio used for?",            "entry")]},
            "genre":       {"name": "genre",           "icon": "▣",
                            "fields": [("v", "music genre (for Suno / Udio)",           "entry")]},
            "mood":        {"name": "mood",            "icon": "◉",
                            "fields": [("v", "vibe and mood of the track",              "entry")]},
            "instruments": {"name": "instruments",     "icon": "◑",
                            "fields": [("v", "key instruments to feature",              "entry")]},
            "tempo":       {"name": "tempo",           "icon": "◷",
                            "fields": [("v", "bpm, pacing, energy level",              "entry")]},
            "vocals":      {"name": "vocals",          "icon": "◎",
                            "fields": [("v", "vocal style, gender, character",          "entry")]},
            "negative":    {"name": "negative",        "icon": "◻",
                            "fields": [("v", "what to exclude",                         "entry")]},
        }
    }
}
