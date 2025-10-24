from fastapi import APIRouter, Request, Response, Query
import random
from ..store import list_canonical_items, get_mock_item_serve
from ..util import randomize_choice_order, make_watermark, canonical_to_serve
from ..util import get_rate_limiter
from ..selection import selection_manager
from .. import selection_repo
import uuid

router = APIRouter()
limiter = get_rate_limiter()

@router.get("/item/next")
@limiter.limit("30/minute")
def get_next_item(
    request: Request,
    response: Response,
    type: str | None = Query(default=None),
    policy: str | None = Query(default=None),
) -> dict:
    session_id = request.cookies.get("ev3_session") or "s_anon"
    items = list_canonical_items()
    if items:
        if session_id == "s_anon":
            canonical = random.choice(items)
        else:
            canonical = selection_manager.next_canonical(session_id, items, target_type=type, policy=policy) or random.choice(items)
        payload = canonical_to_serve(canonical, session_id=session_id)
    else:
        payload = get_mock_item_serve()
    payload = randomize_choice_order(payload)
    payload["serve"]["watermark"] = make_watermark(session_id)
    # Stretch: include serve_id in payload for logging/analytics
    serve_id = f"serve_{uuid.uuid4().hex[:8]}"
    payload["serve"]["id"] = serve_id
    payload["session_id"] = session_id
    # Dev-only event log
    if selection_repo.is_enabled() and session_id != "s_anon":
        selection_repo.append_event({
            "session_id": session_id,
            "item_id": payload.get("item", {}).get("id"),
            "item_type": payload.get("item", {}).get("type"),
            "action": "served",
            "serve_id": serve_id,
        })
    return payload
