from fastapi import APIRouter, Response, Request
import uuid
from ..util import sign_csrf_token
from .. import selection_repo

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
    csrf_token = sign_csrf_token(session_id)
    return {"session_id": session_id, "csrf_token": csrf_token}

@router.get("/progress")
def get_progress(request: Request) -> dict:
    session_id = request.cookies.get(SESSION_COOKIE)
    stats: dict[str, dict[str, int | float]] = {}
    if session_id and selection_repo.is_enabled():
        # Read events from file and aggregate for this session (best-effort)
        try:
            from pathlib import Path
            from ..selection_repo import EVENTS_PATH
            import json
            if EVENTS_PATH.exists():
                with EVENTS_PATH.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            e = json.loads(line)
                        except Exception:
                            continue
                        if e.get("session_id") != session_id:
                            continue
                        item_type = (e.get("item_type") or "unknown").upper()
                        if item_type not in stats:
                            stats[item_type] = {"attempts": 0, "correct": 0, "accuracy": 0.0}
                        if e.get("action") == "answered":
                            stats[item_type]["attempts"] += 1  # type: ignore[index]
                            if bool(e.get("correct")):
                                stats[item_type]["correct"] += 1  # type: ignore[index]
                # compute accuracy
                for t, s in stats.items():
                    a = int(s["attempts"]) or 0
                    c = int(s["correct"]) or 0
                    s["accuracy"] = (c / a) if a > 0 else 0.0
        except Exception:
            stats = {}
    # Provide overall rollup
    overall = {"attempts": 0, "correct": 0, "accuracy": 0.0}
    for s in stats.values():
        overall["attempts"] += int(s["attempts"])  # type: ignore[index]
        overall["correct"] += int(s["correct"])  # type: ignore[index]
    if overall["attempts"] > 0:
        overall["accuracy"] = overall["correct"] / overall["attempts"]
    return {"session_id": session_id, "by_type": stats, "overall": overall}

@router.get("/events.csv")
def export_events_csv(request: Request) -> Response:
    session_id = request.cookies.get(SESSION_COOKIE)
    if not (session_id and selection_repo.is_enabled()):
        return Response(content="ts,session_id,item_id,item_type,action,correct\n", media_type="text/csv")
    try:
        from ..selection_repo import EVENTS_PATH
        import json
        rows = ["ts,session_id,item_id,item_type,action,correct"]
        if EVENTS_PATH.exists():
            with EVENTS_PATH.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                    except Exception:
                        continue
                    if e.get("session_id") != session_id:
                        continue
                    ts = (e.get("ts") or "").replace(",", " ")
                    sid = e.get("session_id") or ""
                    item_id = e.get("item_id") or ""
                    item_type = e.get("item_type") or ""
                    action = e.get("action") or ""
                    correct = "" if (e.get("correct") is None) else ("true" if bool(e.get("correct")) else "false")
                    rows.append(
                        ",".join([ts, sid, item_id, item_type, action, correct])
                    )
        csv_data = "\n".join(rows) + "\n"
        return Response(content=csv_data, media_type="text/csv")
    except Exception:
        return Response(content="ts,session_id,item_id,item_type,action,correct\n", media_type="text/csv")
