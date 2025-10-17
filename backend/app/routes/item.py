from fastapi import APIRouter, Request, Response
import random
from ..store import list_canonical_items, get_mock_item_serve
from ..util import randomize_choice_order, make_watermark, canonical_to_serve
from ..util import get_rate_limiter

router = APIRouter()
limiter = get_rate_limiter()

@router.get("/item/next")
@limiter.limit("5/minute")
def get_next_item(request: Request, response: Response) -> dict:
    session_id = request.cookies.get("ev3_session") or "s_anon"
    items = list_canonical_items()
    if items:
        # Pick a random canonical item each call for simple variety
        canonical = random.choice(items)
        payload = canonical_to_serve(canonical, session_id=session_id)
    else:
        payload = get_mock_item_serve()
    payload = randomize_choice_order(payload)
    payload["serve"]["watermark"] = make_watermark(session_id)
    payload["session_id"] = session_id
    return payload
