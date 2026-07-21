"""Groq (OpenAI-compatible) — generate Short script + image prompts as JSON.

Supports two modes:
  • Single-language preset (legacy): returns full_narration, youtube_title, etc.
  • Multi-variant preset (bilingual): returns image_prompts once + variants[lang] = {title, desc, narration}.
"""
from __future__ import annotations

import json
import os
from typing import Any

from groq import Groq

from pipeline.channel_presets import ChannelPreset
from pipeline.story_history import history_prompt_block
from pipeline.youtube_upload import normalize_description, normalize_tags

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


# ── Language-specific word-count guidance ──────────────────────────────
LANG_WORD_TARGETS = {
    "en": (
        120,
        155,
        "120-155 English words for variants.en.full_narration (~40-50 sec); "
        "add transitions, examples, and a closing takeaway — NOT a bullet list",
    ),
}

DEFAULT_MIN_WORDS = {"en": 80}


def _lang_label(lang: str) -> str:
    return {"en": "English"}.get(lang, lang)


def generate_short_pack(
    preset: ChannelPreset,
    *,
    topic_hint: str | None = None,
    channel_id: str | None = None,
) -> dict[str, Any]:
    topic_hint = (topic_hint or os.environ.get("SHORT_TOPIC", "")).strip()

    user = (
        f"Channel style: {preset['label']}.\n"
        f"Create ONE YouTube Short.\n"
    )
    if topic_hint:
        user += f"Topic idea from creator: {topic_hint}\n"

    if channel_id:
        anti_repeat = history_prompt_block(channel_id)
        if anti_repeat:
            user += anti_repeat

    return _generate_single(preset, user, n)


# ─────────────────────────────────────────────────────────────────────────
# Single-language path (for facts, school_story, history_micro, etc.)
# ─────────────────────────────────────────────────────────────────────────
def _generate_single(preset: ChannelPreset, user: str, n: int) -> dict[str, Any]:
    language = (preset.get("language") or "en").lower()
    lo, hi, blurb = LANG_WORD_TARGETS.get(language, LANG_WORD_TARGETS["en"])

    narration_rule = (
        '"full_narration": "COMPLETE story/script as one continuous paragraph. This is what the voice will read. '
        f'Must be {blurb}. Natural narration — no segment breaks, no numbering."'
    )
    strict_extra = f"- full_narration is ONE continuous paragraph, {lo}-{hi} English words.\n"

    user += f"""
Return ONLY valid JSON with this shape:
{{
  "youtube_title": "short catchy title, under 90 chars, no hashtags",
  "youtube_description": "Detailed 4-5 sentence SEO-optimized summary naturally incorporating high-search-volume keywords and key takeaways, followed by 5-8 viral hashtags at the end including #Shorts",
  "youtube_tags": [
    "keyword1", "keyword2", "keyword3",
    "15 to 20 specific high-ranking search keywords/tags related to this topic (output real tags only, no instruction text)"
  ],
  {narration_rule},
  "image_prompts": [
    "visual description for image 1: setting, subject, action. No style words. No text in image.",
    "visual description for image 2...",
    "..."
  ]
}}

STRICT RULES:
{strict_extra}- "image_prompts" array MUST have exactly {n} entries.
- Each image_prompt matches a different moment/beat in order.
- Image prompts are just visuals — no narration text, no style words, no quotes.
- The narration must flow naturally as one spoken piece (no "segment 1", "segment 2" etc).
"""

    max_attempts = 3
    last_err = ""
    for attempt in range(max_attempts):
        extra = ""
        if attempt > 0:
            extra = (
                f"\n\nCRITICAL: Previous attempt failed validation: {last_err}.\n"
                "Please rewrite the narration to be longer and more detailed. "
                f"Aim for {lo}-{hi} words. Add more descriptive sentences to each beat.\n"
            )

        temp = 0.85 if attempt < 2 else 0.45
        data = _call_groq(preset, user + extra, temperature=temp)

        try:
            narration = data.get("full_narration", "").strip()
            if not narration:
                raise ValueError("Missing full_narration")

            prompts = data.get("image_prompts")
            if not isinstance(prompts, list) or len(prompts) != n:
                raise ValueError(f"Expected {n} image_prompts, got {len(prompts or [])}")
            for i, p in enumerate(prompts):
                if not isinstance(p, str) or not p.strip():
                    raise ValueError(f"image_prompt {i} is empty")

            word_count = len(narration.split())
            min_words = preset.get("min_words", DEFAULT_MIN_WORDS.get(language, 80))
            if word_count < min_words:
                raise ValueError(
                    f"Narration too short ({word_count} words, expected ≥ {min_words} for {language})"
                )

            if not (data.get("youtube_title") or "").strip():
                raise ValueError("Missing youtube_title")
            if not (data.get("youtube_description") or "").strip():
                raise ValueError("Missing youtube_description")
            if not data.get("youtube_tags") or not isinstance(data.get("youtube_tags"), (list, str)):
                raise ValueError("Missing or invalid youtube_tags")

            data["youtube_description"] = normalize_description(data.get("youtube_description"))
            data["youtube_tags"] = normalize_tags(data.get("youtube_tags"))
            return data
        except ValueError as e:
            last_err = str(e)
            if attempt == max_attempts - 1:
                raise

    return data


def _call_groq(
    preset: ChannelPreset,
    user: str,
    *,
    temperature: float = 0.85,
) -> dict[str, Any]:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": preset["groq_system_hint"]},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=3072,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    if not raw:
        raise RuntimeError("Empty Groq response")
    return json.loads(raw)
