from fastapi import APIRouter, Request
from ..store import get_mock_item_serve
from ..util import randomize_choice_order, make_watermark

router = APIRouter()

@router.get("/item/next")
def get_next_item(request: Request) -> dict:
    session_id = request.cookies.get("ev3_session") or "s_anon"
    payload = get_mock_item_serve()
    payload = randomize_choice_order(payload)
    payload["serve"]["watermark"] = make_watermark(session_id)
    payload["session_id"] = session_id
    return payload
