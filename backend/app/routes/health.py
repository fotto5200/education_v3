from fastapi import APIRouter, Response, status
from ..util import get_rate_limiter
from ..store import list_canonical_items
from .. import selection_repo
import os


router = APIRouter()


@router.get("/health")
def health() -> dict:
    # Process up
    return {"status": "ok"}


@router.get("/readiness")
def readiness(response: Response) -> dict:
    # Dev-friendly readiness: always 200, include diagnostics for visibility.
    try:
        limiter = get_rate_limiter()
        _ = getattr(limiter, "key_func", None)
        limiter_ok = _ is not None
    except Exception:
        limiter_ok = False

    # Determine persistence mode from env (no IO)
    def _enabled(val: str | None) -> bool:
        if not isinstance(val, str):
            return False
        v = val.strip().lower()
        return v in ("1", "true", "yes", "on")

    file_enabled = _enabled(os.environ.get("DEV_PERSIST_SELECTION"))
    db_enabled = _enabled(os.environ.get("DB_PERSIST_SELECTION"))

    # In dev, consider persistence ready regardless of mode; routers will lazily init as needed
    items = list_canonical_items()
    seen_types = sorted({(c.get("type") or "").strip().upper() for c in items if isinstance(c.get("type"), str) and c.get("type").strip()})
    diagnostics = {
        "limiter_ok": limiter_ok,
        "persistence": {
            "file": file_enabled,
            "db": db_enabled,
        },
        "canonical": {
            "count": len(items),
            "types": seen_types,
        },
    }
    return {"status": "ready", **diagnostics}


