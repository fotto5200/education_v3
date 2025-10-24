import os
import random
import time
from typing import Dict, Any, List, Optional
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from starlette.requests import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

def randomize_choice_order(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Support both top-level choices and per-step choices
    if "choices" in payload and payload.get("choices"):
        ids = [c.get("id") for c in payload["choices"]]
        random.shuffle(ids)
        payload.setdefault("serve", {})["choice_order"] = ids
    elif payload.get("item", {}).get("steps"):
        # Randomize each step's local order into a parallel array on step.serve.choice_order
        for step in payload["item"]["steps"]:
            ids = [c.get("id") for c in (step.get("choices") or [])]
            random.shuffle(ids)
            step.setdefault("serve", {})["choice_order"] = ids
    return payload


def make_watermark(session_id: str) -> str:
    # lightweight per-serve watermark: session_id + timestamp bucket
    bucket = int(time.time() // 60)
    return f"{session_id}_{bucket}"


def canonical_to_serve(
    canonical: Dict[str, Any],
    *,
    session_id: str,
    media_base_url: str = "/media",
    contract_version: str = "1.0",
) -> Dict[str, Any]:
    """Transform a canonical item (server-only) to a minimal serve snapshot.

    This local adapter uses plain media URLs under /media and a stub ttl_s.
    """
    item_media = []
    for m in canonical.get("media", []) or []:
        object_key = m.get("object_key") or ""
        signed_url = f"{media_base_url}/{object_key}"
        item_media.append({
            "id": m.get("id"),
            "signed_url": signed_url,
            "ttl_s": 120,
            "alt": m.get("alt", "")
        })

    # Build steps (if present) for multi-step items; otherwise use top-level choices
    steps = canonical.get("steps") or []
    serve_steps: List[Dict[str, Any]] = []
    top_level_choices: List[Dict[str, Any]] = []
    if steps:
        for step in steps:
            serve_choices: List[Dict[str, Any]] = []
            for ch in (step.get("choices") or []):
                choice_media = []
                for cm in (ch.get("media") or []):
                    object_key = cm.get("object_key") or ""
                    signed_url = f"{media_base_url}/{object_key}"
                    choice_media.append({
                        "id": cm.get("id"),
                        "signed_url": signed_url,
                        "ttl_s": 120,
                        "alt": cm.get("alt", ""),
                    })
                payload_choice: Dict[str, Any] = {"id": ch.get("id"), "text": ch.get("text")}
                if choice_media:
                    payload_choice["media"] = choice_media
                serve_choices.append(payload_choice)

            serve_steps.append(
                {
                    "step_id": step.get("step_id"),
                    "prompt": {"html": (step.get("prompt") or {}).get("html", "")},
                    "choices": serve_choices,
                }
            )
    else:
        # Single-step/simple item: expose choices at the top level (with optional media)
        for ch in (canonical.get("steps") or [{}])[0].get("choices", []) if canonical.get("steps") else []:
            payload_choice = {"id": ch.get("id"), "text": ch.get("text")}
            choice_media = []
            for cm in (ch.get("media") or []):
                object_key = cm.get("object_key") or ""
                signed_url = f"{media_base_url}/{object_key}"
                choice_media.append({
                    "id": cm.get("id"),
                    "signed_url": signed_url,
                    "ttl_s": 120,
                    "alt": cm.get("alt", ""),
                })
            if choice_media:
                payload_choice["media"] = choice_media
            top_level_choices.append(payload_choice)  # type: ignore[arg-type]

    serve_payload: Dict[str, Any] = {
        "version": contract_version,
        "session_id": session_id,
        "item": {
            "id": canonical.get("id", "i_local"),
            "type": canonical.get("type", "mcq"),
            "title": canonical.get("title"),
            "content": {"html": (canonical.get("content") or {}).get("html", "")},
            "media": item_media,
        } | ({"steps": serve_steps} if serve_steps else {}),
        **({"choices": top_level_choices} if not serve_steps else {}),
        "serve": {"seed": f"s{random.randint(1000,9999)}", "choice_order": [], "watermark": ""},
        "ui": {"layout": "question-above-choices", "actions": ["submit"]},
    }
    return serve_payload


# --- CSRF helpers ---

def _get_csrf_secret() -> str:
    return os.environ.get("CSRF_SECRET", "dev-secret")


def sign_csrf_token(session_id: str) -> str:
    serializer = URLSafeTimedSerializer(_get_csrf_secret(), salt="csrf")
    return serializer.dumps({"sid": session_id})


def verify_csrf_token(token: str, session_id: str, max_age_s: int = 3600) -> bool:
    serializer = URLSafeTimedSerializer(_get_csrf_secret(), salt="csrf")
    try:
        data = serializer.loads(token, max_age=max_age_s)
        return isinstance(data, dict) and data.get("sid") == session_id
    except (BadSignature, SignatureExpired):
        return False


# --- Rate limiter (singleton) ---
_rate_limiter: Optional[Limiter] = None


def _limiter_key_func(request: Request) -> str:
    session_id = request.cookies.get("ev3_session")
    return session_id or get_remote_address(request)


def get_rate_limiter() -> Limiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = Limiter(
            key_func=_limiter_key_func,
            headers_enabled=True,
        )
    return _rate_limiter
