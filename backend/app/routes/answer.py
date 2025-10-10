from fastapi import APIRouter
from pydantic import BaseModel
from ..store import get_mock_submit_result

router = APIRouter()

class SubmitStep(BaseModel):
    session_id: str
    item_id: str
    step_id: str | None = None
    choice_id: str | None = None

@router.post("/answer")
def submit_step(body: SubmitStep) -> dict:
    # For now, return a mock grading result; real logic will check correctness server-side
    return get_mock_submit_result()
