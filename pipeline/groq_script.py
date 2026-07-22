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

SEO_SYSTEM_PROMPT = """You are a YouTube Shorts SEO expert specializing in Automotive, Cars, and Formula 1 content.

Rules for Title:
- Keep under 60 characters for mobile display.
- Place the strongest hook keyword (e.g., "F1", "Bugatti", "Ferrari", "Car Myth") in the first 3 words.
- Use curiosity gaps or bold claims (e.g., "The Secret Reason F1 Cars Cost $15M").

Rules for Tags:
- Generate 10-12 tags as comma-separated values.
- Mix broad tags (#cars, #f1, #automotive) with specific niche tags (#ferrarimotorsport, #carhistory).
- Include high-volume terms: "car facts", "automotive history", "racing trivia"."""


HOOK_PROMPT = """Create a 3-second opening hook for a YouTube Short about {topic}.
Must start with an action verb, a controversial question, or a surprising number.
Examples:
- "Why did Ford spend $25 Million just to beat Ferrari?"
- "This single F1 rule changed racing forever."
Do NOT say "Hey guys" or "Welcome back"."""


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


def generate_youtube_description(video_summary: str, tags_list: list[str]) -> str:
    tag0 = tags_list[0] if len(tags_list) > 0 else "automotive"
    tag1 = tags_list[1] if len(tags_list) > 1 else "carfacts"
    description = f"""
{video_summary}

🏎️ Subscribe for daily Automotive Facts, F1 Secrets, and Car History!
👇 Comment your favorite car below!

---
TIMESTAMPS / TOPICS:
0:00 - {video_summary[:50]}...

RELATED SEARCHES:
#cars #f1 #automotive #carfacts #racing #supercars #{tag0} #{tag1}
"""
    return description


def generate_opening_hook(preset: ChannelPreset, topic: str) -> str:
    """Generate a dedicated 3-second opening hook right before generating the main script."""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompt = HOOK_PROMPT.format(topic=topic)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a viral YouTube Shorts script writer specializing in killer hooks."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.85,
        max_tokens=60,
    )
    raw = (resp.choices[0].message.content or "").strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1].strip()
    return raw


def generate_short_pack(
    preset: ChannelPreset,
    *,
    topic_hint: str | None = None,
    channel_id: str | None = None,
) -> dict[str, Any]:
    topic_hint = (topic_hint or os.environ.get("SHORT_TOPIC", "")).strip()

    hook_topic = topic_hint or preset.get("label", "Automotive & F1 Facts")
    try:
        print("①-A Hook Generator: generating 3-second opening hook…")
        opening_hook = generate_opening_hook(preset, hook_topic)
        print(f"   Opening Hook: {opening_hook!r}")
    except Exception as e:
        print(f"   ⚠ Hook generation fallback due to: {e}")
        opening_hook = ""

    user = (
        f"Channel style: {preset['label']}.\n"
        f"Create ONE YouTube Short.\n"
    )
    if topic_hint:
        user += f"Topic idea from creator: {topic_hint}\n"
    if opening_hook:
        user += (
            f"MANDATORY OPENING HOOK (First 3 seconds): Must start full_narration EXACTLY with this sentence: "
            f'"{opening_hook}" Followed by the rest of the high-retention story.\n'
        )

    if channel_id:
        anti_repeat = history_prompt_block(channel_id)
        if anti_repeat:
            user += anti_repeat

    n = int(preset.get("segment_count", 5))
    pack = _generate_single(preset, user, n)
    if opening_hook:
        pack["opening_hook"] = opening_hook
    return pack


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
  "youtube_title": "short catchy title under 60 chars, strongest hook keyword (e.g. 'F1', 'Bugatti', 'Ferrari') in first 3 words, no hashtags",
  "youtube_description": "Detailed 4-5 sentence SEO-optimized summary naturally incorporating high-search-volume keywords and key takeaways, followed by 5-8 viral hashtags at the end including #Shorts",
  "youtube_tags": [
    "cars", "f1", "ferrarimotorsport", "car facts",
    "10-12 specific tags mixing broad tags, specific niche tags (#ferrarimotorsport, #carhistory), and high-volume terms ('car facts', 'automotive history', 'racing trivia')"
  ],
  {narration_rule},
  "image_prompts": [
    "visual description for image 1: setting, subject, action. No style words. No text in image.",
    "visual description for image 2...",
    "..."
  ]
}}

STRICT RULES:
{strict_extra}- "youtube_title" MUST be under 60 characters with the strongest hook keyword in the first 3 words and use curiosity gaps or bold claims.
- "youtube_tags" MUST have 10-12 tags mixing broad tags (#cars, #f1, #automotive), niche tags (#ferrarimotorsport, #carhistory), and high-volume terms ("car facts", "automotive history", "racing trivia").
- "image_prompts" array MUST have exactly {n} entries.
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
                if attempt == max_attempts - 1 and word_count >= 80:
                    print(f"   ⚠ Narration word count ({word_count}) is under target ({min_words}), but ≥ 80 words — accepting on final attempt.")
                else:
                    raise ValueError(
                        f"Narration too short ({word_count} words, expected ≥ {min_words} for {language})"
                    )

            if not (data.get("youtube_title") or "").strip():
                raise ValueError("Missing youtube_title")
            if not (data.get("youtube_description") or "").strip():
                raise ValueError("Missing youtube_description")
            if not data.get("youtube_tags") or not isinstance(data.get("youtube_tags"), (list, str)):
                raise ValueError("Missing or invalid youtube_tags")

            tags_list = normalize_tags(data.get("youtube_tags"))
            raw_summary = (data.get("youtube_description") or "").strip()
            structured_desc = generate_youtube_description(raw_summary, tags_list)
            data["youtube_tags"] = tags_list
            data["youtube_description"] = normalize_description(structured_desc)
            return data
        except ValueError as e:
            last_err = str(e)
            if attempt == max_attempts - 1:
                raise

    tags_list = normalize_tags(data.get("youtube_tags"))
    raw_summary = (data.get("youtube_description") or "").strip()
    structured_desc = generate_youtube_description(raw_summary, tags_list)
    data["youtube_tags"] = tags_list
    data["youtube_description"] = normalize_description(structured_desc)
    return data


def _call_groq(
    preset: ChannelPreset,
    user: str,
    *,
    temperature: float = 0.85,
) -> dict[str, Any]:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    system_content = f"{preset['groq_system_hint']}\n\n{SEO_SYSTEM_PROMPT}"
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_content},
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


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    from pipeline.channel_presets import get_preset, list_channel_ids

    parser = argparse.ArgumentParser(description="Test Groq script generation.")
    parser.add_argument("--channel", default="school_story", choices=list_channel_ids(), help="Channel preset to test")
    parser.add_argument("--topic", default="", help="Optional topic hint")
    args = parser.parse_args()

    preset = get_preset(args.channel)
    print(f"Generating script for channel '{args.channel}' using Groq ({GROQ_MODEL})...")
    result = generate_short_pack(preset, topic_hint=args.topic, channel_id=args.channel)
    print("\n--- Generated Output JSON ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

