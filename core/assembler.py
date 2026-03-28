"""
PromptForge — core/assembler.py
Pure prompt assembly logic. No UI dependencies.

WEIGHT SYNTAX:
  Each model declares a weight_syntax in modes.py:
    "none"  — weights ignored, plain text output
    "a1111" — (word:1.4) syntax (SDXL, A1111)
    "mj"    — word::2 syntax (Midjourney)

  Weights only apply when the slider value is above 1.0 + threshold.
  At exactly 1.0 the text is output plain regardless of syntax.

ASSEMBLY ORDER:
  User drag order = assembly order.
  Model order = starting default only (set on tab init).
  Priority overrides (badge) force numeric position.

by daGonen
"""

from data.modes import MODES

# Weight only kicks in above this threshold to avoid wrapping everything
WEIGHT_THRESHOLD = 1.05


def get_assembly_order(mode: str, model_key: str, active_blocks: list, priorities: dict) -> list:
    """
    Return the assembly order for the current block list.

    Rules:
      1. Blocks with a manual priority override sort by numeric value first.
      2. All 'auto' blocks keep their position in active_blocks (drag order).
      3. 'negative' always goes last.
    """
    overridden  = []
    auto_ordered = []

    for k in active_blocks:
        p = priorities.get(k, "auto")
        if p != "auto":
            try:
                overridden.append((int(p), k))
            except ValueError:
                auto_ordered.append(k)
        else:
            auto_ordered.append(k)

    overridden.sort(key=lambda x: x[0])

    if not overridden:
        result = list(active_blocks)
    else:
        result = list(auto_ordered)
        for priority, key in overridden:
            insert_at = min(priority, len(result))
            result.insert(insert_at, key)

    # negative always last
    if "negative" in result:
        result.remove("negative")
        result.append("negative")

    return result


def get_default_order(mode: str, model_key: str, available_blocks: list) -> list:
    """
    Sort blocks by model's preferred order.
    Used only when initialising a fresh tab — sets the starting drag order.
    """
    model_order = MODES[mode]["models"][model_key]["order"]

    def rank(k):
        return model_order.index(k) if k in model_order else 99

    return sorted(available_blocks, key=rank)


def _apply_weight(text: str, weight: float, syntax: str) -> str:
    """
    Wrap text in model-specific weight syntax.
    Only applies if weight is meaningfully above 1.0.

    a1111: (text:1.4)
    mj:    text::2       — MJ uses integers, rounds to nearest
    none:  text          — returned as-is
    """
    if syntax == "none" or weight < WEIGHT_THRESHOLD:
        return text

    if syntax == "a1111":
        return f"({text}:{weight:.1f})"

    if syntax == "mj":
        # Midjourney uses integer weights (::1, ::2, ::3...)
        # Map 1.0–1.3 → ::1, 1.4–1.6 → ::2, 1.7+ → ::3
        if weight < 1.4:
            w = 1
        elif weight < 1.7:
            w = 2
        else:
            w = 3
        return f"{text}::{w}"

    return text


def build_prompt(mode: str, model_key: str, active_blocks: list,
                 priorities: dict, vals: dict) -> tuple[str, str]:
    """
    Assemble the final prompt and negative prompt strings.
    Applies weight syntax per model for blocks that have a weight field.

    Returns:
        (prompt, negative) — both plain strings, ready to copy.
    """
    ordered  = get_assembly_order(mode, model_key, active_blocks, priorities)
    model    = MODES[mode]["models"][model_key]
    syntax   = model.get("weight_syntax", "none")
    parts    = []
    negative = ""

    for k in ordered:
        block_vals = vals.get(k, {})
        text = block_vals.get("v", "").strip()
        if not text:
            continue

        if k == "negative":
            negative = text
            continue

        # Apply weight if this block has a weight field and model supports it
        weight = block_vals.get("w", 1.0)
        try:
            weight = float(weight)
        except (TypeError, ValueError):
            weight = 1.0

        parts.append(_apply_weight(text, weight, syntax))

    return ", ".join(parts), negative


def count_tokens(text: str) -> int:
    """Rough token count — word-based approximation."""
    return len(text.strip().split()) if text.strip() else 0


def token_budget_status(mode: str, model_key: str, prompt: str) -> dict:
    """
    Return token budget info for the UI.
    Returns dict: tokens, budget, pct, optimal, label, status
    """
    m      = MODES[mode]["models"][model_key]
    tokens = count_tokens(prompt)
    budget = m["budget"]
    pct    = tokens / budget if budget else 0.0

    if pct > 1.0:
        status = "over"
    elif pct > 0.85:
        status = "warning"
    else:
        status = "ok"

    return {
        "tokens":  tokens,
        "budget":  budget,
        "pct":     min(pct, 1.0),
        "optimal": m["optimal"],
        "label":   m["label"],
        "status":  status,
    }


def get_order_issues(mode: str, model_key: str, active_blocks: list, priorities: dict) -> list:
    """
    Returns a list of dicts for every block that is out of model-preferred position.
    Only checks blocks with priority = 'auto' (manual overrides are intentional).

    Each issue dict:
        {
            "key":       block key string,
            "name":      display name,
            "current":   current index in active_blocks (0-based),
            "preferred": preferred index in model order (0-based, among active blocks only),
        }

    Uses preferred index among ACTIVE blocks only — not the full model order list.
    This avoids false positives when optional blocks are not added.
    """
    model_order = MODES[mode]["models"][model_key]["order"]
    bd          = MODES[mode]["blocks"]

    # Build the model-preferred order restricted to active blocks only
    preferred_order = [k for k in model_order if k in active_blocks]
    # Blocks not in model_order go at end in their current position
    extras = [k for k in active_blocks if k not in model_order]
    preferred_order = preferred_order + extras

    issues = []
    for current_idx, k in enumerate(active_blocks):
        if priorities.get(k, "auto") != "auto":
            continue  # manual override — intentional, skip
        if k not in preferred_order:
            continue
        preferred_idx = preferred_order.index(k)
        if current_idx != preferred_idx:
            issues.append({
                "key":       k,
                "name":      bd[k]["name"] if k in bd else k,
                "current":   current_idx,
                "preferred": preferred_idx,
            })

    return issues


def model_supports_weights(mode: str, model_key: str) -> bool:
    """
    Returns True if this model uses weight syntax.
    Used by BlockWidget to decide whether to show the weight slider.
    """
    syntax = MODES[mode]["models"][model_key].get("weight_syntax", "none")
    return syntax != "none"


def weight_syntax_label(mode: str, model_key: str) -> str:
    """
    Returns a human-readable label for the weight syntax.
    Used as the slider label in the UI.
    """
    syntax = MODES[mode]["models"][model_key].get("weight_syntax", "none")
    if syntax == "a1111":
        return "emphasis  (word:1.x)"
    if syntax == "mj":
        return "emphasis  (word::n)"
    return "emphasis weight"
