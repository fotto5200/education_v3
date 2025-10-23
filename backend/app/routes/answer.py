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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="csrf_required")

    canonical = get_canonical_by_id(body.item_id or "")
    if not canonical:
        # Fallback to mock result if item not found (dev)
        result = get_mock_submit_result()
        canonical_type = None
    else:
        canonical_type = canonical.get("type")
        # Step-aware grading (dev): prefer steps[].correct_choice_id when present for the targeted step.
        # Fallback: compare submitted choice text against final.answer_text.
        final_answer = ((canonical.get("final") or {}).get("answer_text") or "").strip()
        explanation_html = ((canonical.get("final") or {}).get("explanation") or {}).get("html")

        steps = canonical.get("steps") or []
        correct: bool | None = None

        if steps:
            # Determine target step (default to first if unspecified or missing)
            target_step = None
            if body.step_id:
                for s in steps:
                    if s.get("step_id") == body.step_id:
                        target_step = s
                        break
            if target_step is None:
                target_step = steps[0]

            correct_choice_id = target_step.get("correct_choice_id")
            if isinstance(correct_choice_id, str) and correct_choice_id:
                # Grade by id when available
                correct = (body.choice_id == correct_choice_id)
            else:
                # Fallback by text match within the step's choices
                submitted_text = None
                for ch in (target_step.get("choices") or []):
                    if ch.get("id") == body.choice_id:
                        submitted_text = (ch.get("text") or "").strip()
                        break
                if submitted_text is not None and final_answer:
                    correct = (submitted_text == final_answer)

        if correct is None:
            # No steps model or could not resolve step: try top-level choices (legacy) then final.answer_text
            submitted_text = None
            if isinstance(canonical.get("choices"), list):
                for ch in canonical.get("choices"):
                    if ch.get("id") == body.choice_id:
                        submitted_text = (ch.get("text") or "").strip()
                        break
            if submitted_text is not None and final_answer:
                correct = (submitted_text == final_answer)
            else:
                correct = False

        result = {"correct": bool(correct)}
        if explanation_html:
            result["explanation"] = {"html": explanation_html}

    # Dev-only event log
    if selection_repo.is_enabled() and session_id:
        selection_repo.append_event({
            "session_id": session_id,
            "item_id": body.item_id,
            "item_type": canonical_type,
            "action": "answered",
            "correct": bool(result.get("correct")),
        })
    return result
