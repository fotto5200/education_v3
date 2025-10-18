from fastapi import APIRouter, Header, Request, HTTPException, status, Response
from pydantic import BaseModel
from ..store import get_mock_submit_result
from ..util import verify_csrf_token
from ..util import get_rate_limiter
from .. import selection_repo

router = APIRouter()
limiter = get_rate_limiter()

class SubmitStep(BaseModel):
    session_id: str
    item_id: str
    step_id: str | None = None
    choice_id: str | None = None

@router.post("/answer")
@limiter.limit("30/minute")
def submit_step(
    body: SubmitStep,
    request: Request,
    response: Response,
    x_csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> dict:
    session_id = request.cookies.get("ev3_session")
    if not session_id or not x_csrf_token or not verify_csrf_token(x_csrf_token, session_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF required")
    # For now, return a mock grading result; real logic will check correctness server-side
    result = get_mock_submit_result()
    # Dev-only event log
    if selection_repo.is_enabled() and session_id:
        selection_repo.append_event({
            "session_id": session_id,
            "item_id": body.item_id,
            "item_type": None,
            "action": "answered",
            "correct": bool(result.get("correct")),
        })
    return result
