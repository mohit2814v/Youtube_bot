"""Upload MP4 to YouTube via OAuth2.

Works in two modes:
  Local:  reads secrets/client_secret.json + secrets/youtube_token.json
  CI/CD:  reads YT_CLIENT_ID, YT_CLIENT_SECRET_VALUE, YT_REFRESH_TOKEN from env
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _creds_from_env(refresh_token_env: str = "YT_REFRESH_TOKEN") -> Credentials | None:
    """Reconstruct credentials from GitHub Actions secrets.

    The client_id/secret are shared (same OAuth app authorizes multiple channels),
    but each YouTube channel has its own refresh token stored under a distinct env var name.
    """
    client_id = os.environ.get("YT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YT_CLIENT_SECRET_VALUE", "").strip()
    refresh_token = os.environ.get(refresh_token_env, "").strip()
    # Fallback to the default token if a channel-specific one is empty
    if not refresh_token and refresh_token_env != "YT_REFRESH_TOKEN":
        refresh_token = os.environ.get("YT_REFRESH_TOKEN", "").strip()
    if not (client_id and client_secret and refresh_token):
        return None
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=TOKEN_URI,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )


def _creds_from_files(client_secret_path: Path, token_path: Path) -> Credentials:
    """Local development: token file + optional browser OAuth flow."""
    creds: Credentials | None = None
    if token_path.is_file():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not client_secret_path.is_file():
                raise FileNotFoundError(
                    f"Missing {client_secret_path}. Run: python scripts/youtube_auth.py"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds


def _get_creds(refresh_token_env: str = "YT_REFRESH_TOKEN") -> Credentials:
    creds = _creds_from_env(refresh_token_env)
    if creds:
        try:
            creds.refresh(Request())
        except RefreshError as e:
            raise RuntimeError(
                f"\n\n❌ {refresh_token_env} is invalid or expired.\n"
                "   Common cause: OAuth consent screen is in 'Testing' mode "
                "(tokens expire after 7 days).\n\n"
                "   FIX:\n"
                "   1. Go to https://console.cloud.google.com/apis/credentials/consent\n"
                "      → click PUBLISH APP (ignore the 'Needs verification' warning).\n"
                "   2. Regenerate locally:  python scripts/youtube_auth.py\n"
                f"   3. Update GitHub secret {refresh_token_env} with the new value.\n\n"
                f"   Underlying error: {e}"
            ) from e
        return creds
    client_secret = Path(os.environ.get("YT_CLIENT_SECRET", "secrets/client_secret.json"))
    token = Path(os.environ.get("YT_TOKEN", "secrets/youtube_token.json"))
    return _creds_from_files(client_secret, token)


def normalize_tags(tags: Any) -> list[str]:
    """Normalize and sanitize tags for YouTube API v3 (max 30 tags, max 100 chars each, max 450 total chars)."""
    if not tags:
        return []
    if isinstance(tags, str):
        s = tags.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    tags = parsed
            except Exception:
                pass
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.replace("\n", ",").split(",") if t.strip()]
    elif not isinstance(tags, (list, tuple)):
        return []

    cleaned: list[str] = []
    seen: set[str] = set()
    total_len = 0
    for t in tags:
        if not isinstance(t, str):
            t = str(t)
        t = t.strip()
        if t.startswith("#"):
            t = t[1:].strip()
        t = "".join(c for c in t if c not in '<>"').strip()
        if not t:
            continue
        if len(t) > 100:
            t = t[:100].strip()
        t_lower = t.lower()
        if t_lower in seen:
            continue
        if total_len + len(t) + 2 > 450 or len(cleaned) >= 30:
            break
        cleaned.append(t)
        seen.add(t_lower)
        total_len += len(t) + 2
    return cleaned


def normalize_description(description: Any) -> str:
    """Normalize and truncate description to within YouTube API limit (max 5000 chars)."""
    if not description:
        return ""
    if not isinstance(description, str):
        description = str(description)
    return description.strip()[:5000]


def upload_short(
    video_path: Path,
    title: str,
    description: str,
    *,
    tags: list[str] | str | None = None,
    privacy_status: str = "private",
    category_id: str = "24",
    refresh_token_env: str = "YT_REFRESH_TOKEN",
) -> str:
    """Upload and return YouTube video ID.

    Pass `refresh_token_env` to target a different channel (e.g. "YT_REFRESH_TOKEN_HI").
    Falls back to YT_REFRESH_TOKEN if the named env var is unset.
    """
    creds = _get_creds(refresh_token_env)
    youtube = build("youtube", "v3", credentials=creds)
    norm_desc = normalize_description(description)
    norm_tags = normalize_tags(tags)
    body = {
        "snippet": {
            "title": title[:100],
            "description": norm_desc,
            "categoryId": category_id,
            "tags": norm_tags,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = req.next_chunk()
    if not response or "id" not in response:
        raise RuntimeError(f"Unexpected YouTube API response: {response!r}")
    return str(response["id"])
