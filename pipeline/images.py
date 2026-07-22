"""Image generation via DeAPI.ai (async: submit → poll → download)."""
from __future__ import annotations

import os
import random
import time
from pathlib import Path

import httpx

DEAPI_SUBMIT_URL = "https://api.deapi.ai/api/v1/client/txt2img"
DEAPI_POLL_URL = "https://api.deapi.ai/api/v1/client/request-status"

STYLE_SUFFIX = (
    ", cinematic digital illustration, detailed scene art, strong composition, "
    "professional youtube visual quality, no text, no captions, no watermark, no logos"
)

DEFAULT_NEGATIVE = (
    "blurry, low quality, watermark, logo, text, title, signature, ugly, grainy, "
    "gore, blood, nudity, child-unsafe"
)


def full_visual_prompt(scene: str, style_suffix: str | None = None) -> str:
    """Combine the scene description with a channel-specific style suffix."""
    return f"{scene.strip()}{(style_suffix or STYLE_SUFFIX)}"


def _deapi_generate(
    prompt: str,
    *,
    api_key: str,
    width: int,
    height: int,
    model: str,
    max_polls: int = 30,
    poll_interval: float = 3.0,
) -> bytes:
    """Submit image job, poll until done, download result."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Step 1: Submit
    payload = {
        "prompt": prompt,
        "model": model,
        "width": width,
        "height": height,
        "steps": 4,
        "seed": random.randint(1, 999999),
    }

    with httpx.Client(timeout=60.0) as client:
        # Submit with retry on 429 and timeouts/network errors
        resp = None
        for submit_try in range(5):
            try:
                resp = client.post(DEAPI_SUBMIT_URL, json=payload, headers=headers)
                if resp.status_code == 429:
                    wait = 15 * (submit_try + 1)
                    print(f"      DeAPI 429 on submit — waiting {wait}s (try {submit_try + 1}/5)…")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                break
            except (httpx.TimeoutException, httpx.TransportError) as e:
                wait = 5 * (submit_try + 1)
                print(f"      DeAPI timeout/network error on submit ({e}) — waiting {wait}s (try {submit_try + 1}/5)…")
                time.sleep(wait)
                if submit_try == 4:
                    raise
        if resp is None:
            raise RuntimeError("DeAPI: failed on submit after 5 retries")

        data = resp.json()

        request_id = data.get("data", {}).get("request_id")
        if not request_id:
            raise RuntimeError(f"No request_id in DeAPI response: {data}")
        print(f"      DeAPI submitted (id: {request_id})")

        # Step 2: Poll
        poll_headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        for attempt in range(1, max_polls + 1):
            time.sleep(poll_interval)

            try:
                poll_resp = client.get(
                    f"{DEAPI_POLL_URL}/{request_id}",
                    headers=poll_headers,
                    timeout=30.0,
                )
                poll_resp.raise_for_status()
                poll_data = poll_resp.json()
            except (httpx.TimeoutException, httpx.TransportError) as e:
                print(f"      DeAPI poll timeout/network error on attempt {attempt}/{max_polls} ({e}) — retrying…")
                continue

            status = poll_data.get("data", {}).get("status", "")

            if status in ("completed", "success", "done"):
                image_url = poll_data["data"].get("result_url")
                if not image_url:
                    raise RuntimeError(f"Completed but no result_url: {poll_data}")

                for download_try in range(5):
                    try:
                        img_resp = client.get(image_url, timeout=60.0)
                        img_resp.raise_for_status()
                        break
                    except (httpx.TimeoutException, httpx.TransportError) as e:
                        wait = 3 * (download_try + 1)
                        print(f"      DeAPI image download timeout ({e}) — waiting {wait}s (try {download_try + 1}/5)…")
                        time.sleep(wait)
                        if download_try == 4:
                            raise

                print(f"      DeAPI done (polled {attempt}x)")
                return img_resp.content

            if status in ("failed", "error"):
                raise RuntimeError(f"DeAPI image failed: {poll_data}")

            # Still processing — keep polling

        raise RuntimeError(f"DeAPI timed out after {max_polls} polls for {request_id}")


def save_scene_image(
    index: int,
    prompt: str,
    out_path: Path,
    *,
    width: int = 768,
    height: int = 768,
    negative: str = DEFAULT_NEGATIVE,
) -> tuple[str, str]:
    """Generate and save one image. Returns (status, detail). Retries up to 3 times."""
    api_key = os.environ.get("DEAPI_TOKEN", "").strip()
    if not api_key:
        return "fail", "DEAPI_TOKEN not set"

    model = os.environ.get("DEAPI_MODEL", "Flux_2_Klein_4B_BF16")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    last_err = "Unknown error"
    for try_num in range(1, 4):
        try:
            img_bytes = _deapi_generate(
                prompt,
                api_key=api_key,
                width=width,
                height=height,
                model=model,
            )
            out_path.write_bytes(img_bytes)
            return "ok", "deapi"
        except Exception as e:
            last_err = str(e)
            if try_num < 3:
                wait = 5 * try_num
                print(f"   ⚠ Image {index} attempt {try_num}/3 failed ({last_err}) — retrying in {wait}s…")
                time.sleep(wait)

    return "fail", last_err
