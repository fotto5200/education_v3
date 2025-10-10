from fastapi import APIRouter, Response
import uuid

router = APIRouter()

SESSION_COOKIE = "ev3_session"

@router.post("/session")
def create_session(response: Response) -> dict:
    session_id = f"s_{uuid.uuid4().hex[:8]}"
    # httpOnly cookie; secure flag can be toggled in prod
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    return {"session_id": session_id}
