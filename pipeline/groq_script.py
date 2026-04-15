"""Groq (OpenAI-compatible) — generate Short script + image prompts as JSON."""
from __future__ import annotations

import json
import os
from typing import Any

from groq import Groq

from pipeline.channel_presets import ChannelPreset
from pipeline.story_history import history_prompt_block

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


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

    n = preset["segment_count"]
    user += f"""
Return ONLY valid JSON with this shape:
{{
  "youtube_title": "short catchy title, under 90 chars, no hashtags",
  "youtube_description": "2-3 sentences plus optional #Shorts at end",
  "full_narration": "The COMPLETE story/script as one continuous paragraph. This is what the voice will read. Must be 120-150 words (35-45 seconds when read aloud at normal pace). Write it as natural spoken narration — no segment breaks, no numbering.",
  "image_prompts": [
    "visual description for image 1: setting, characters, action. No style words. No text in image.",
    "visual description for image 2...",
    "..."
  ]
}}

STRICT RULES:
- "full_narration" is ONE continuous paragraph, 120-150 words total. This is critical for audio length.
- "image_prompts" array MUST have exactly {n} entries.
- Each image_prompt should match a different moment/beat of the story in order.
- Image prompts are just visuals — no narration text, no style words, no quotes.
- The narration must flow naturally as one spoken piece (no "segment 1", "segment 2" etc).
"""

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": preset["groq_system_hint"]},
            {"role": "user", "content": user},
        ],
        temperature=0.85,
        max_tokens=2048,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    if not raw:
        raise RuntimeError("Empty Groq response")
    data = json.loads(raw)

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
    if word_count < 80:
        raise ValueError(f"Narration too short ({word_count} words, need 120-150)")

    return data
