"""Channel niches: system prompt + defaults for Groq script generation.

Good Shorts lanes (2–4 channels):
- facts: high search intent, easy to batch (competitive).
- school_story: narrative retention, strong watch time if hooks are good.
- psychology: "why you feel X" hooks (sensitive—avoid medical claims).
- history_micro: one date / one person / one battle (watch copyright on clips).

You still need distinct value (editing, series, niche focus); pure spam risks strikes.
"""

from __future__ import annotations

from typing import TypedDict


class ChannelPreset(TypedDict):
    id: str
    label: str
    groq_system_hint: str
    segment_count: int  # images + script beats


PRESETS: dict[str, ChannelPreset] = {
    "facts": {
        "id": "facts",
        "label": "5 interesting facts (general)",
        "groq_system_hint": (
            "You write punchy YouTube Shorts. Niche: surprising facts, curious trivia. "
            "Tone: energetic but clear, no clickbait lies. Each fact must be broadly accurate; "
            "if unsure, pick safer wording. No hashtags inside narration."
        ),
        "segment_count": 5,
    },
    "school_story": {
        "id": "school_story",
        "label": "School drama / storytime Short",
        "groq_system_hint": (
            "You write fictional school storytime Shorts. Tone: suspense + heart. "
            "Characters are original (no copyrighted names). Hook in line 1. "
            "Build to one memorable twist. Keep each kid-safe."
        ),
        "segment_count": 5,
    },
    "psych_tradeoff": {
        "id": "psych_tradeoff",
        "label": "Psychology / habits (non-clinical)",
        "groq_system_hint": (
            "You write Shorts about habits, motivation, and everyday psychology. "
            "Never diagnose or claim medical facts. Use 'some people' / 'research suggests' carefully. "
            "Practical tips only."
        ),
        "segment_count": 5,
    },
    "history_micro": {
        "id": "history_micro",
        "label": "One moment in history",
        "groq_system_hint": (
            "You write one tight historical anecdote per Short. Pick public-domain or widely taught events. "
            "No graphic violence. End with why it matters in one line."
        ),
        "segment_count": 5,
    },
    "ghost_stories": {
        "id": "ghost_stories",
        "label": "Ghost / horror storytime Short",
        "groq_system_hint": (
            "You write spooky ghost story Shorts for YouTube. "
            "CRITICAL LENGTH RULE: The TOTAL word count across ALL 6 segments MUST be 120-140 words. "
            "Each segment narration = 2-3 sentences, about 20-25 words per segment. "
            "This produces 35-45 seconds of audio when read aloud. "
            "Tone: eerie, suspenseful, creepy but NOT gory or violent. "
            "Segment 1: hook that stops scrolling. Last segment: chilling twist or unanswered question. "
            "All stories fictional. Original characters. PG-13. No hashtags in narration."
        ),
        "segment_count": 6,
    },
}


def list_channel_ids() -> list[str]:
    return sorted(PRESETS.keys())


def get_preset(channel_id: str) -> ChannelPreset:
    key = channel_id.strip().lower().replace("-", "_")
    if key not in PRESETS:
        raise KeyError(f"Unknown channel preset {channel_id!r}. Try: {', '.join(list_channel_ids())}")
    return PRESETS[key]
