from fastapi import APIRouter, Header, Request, HTTPException, status, Response
from pydantic import BaseModel
from ..store import get_mock_submit_result, get_canonical_by_id
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

    canonical = get_canonical_by_id(body.item_id or "")
    if not canonical:
        # Fallback to mock result if item not found (dev)
        result = get_mock_submit_result()
    else:
        # Minimal grading: match selected choice text against final.answer_text (trimmed, case-sensitive for now)
        final_answer = ((canonical.get("final") or {}).get("answer_text") or "").strip()
        explanation_html = ((canonical.get("final") or {}).get("explanation") or {}).get("html")
        # Find submitted choice text from either top-level choices or step choices
        submitted_text = None
        steps = canonical.get("steps") or []
        if steps:
            for step in steps:
                for ch in (step.get("choices") or []):
                    if ch.get("id") == body.choice_id:
                        submitted_text = (ch.get("text") or "").strip()
                        break
                if submitted_text is not None:
                    break
        # If no steps model, try top-level choices structure (not typical for canonical)
        if submitted_text is None and isinstance(canonical.get("choices"), list):
            for ch in canonical.get("choices"):
                if ch.get("id") == body.choice_id:
                    submitted_text = (ch.get("text") or "").strip()
                    break
        correct = bool(submitted_text) and (submitted_text == final_answer)
        result = {"correct": correct}
        if explanation_html:
            result["explanation"] = {"html": explanation_html}

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
