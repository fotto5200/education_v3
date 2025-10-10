import random
import time
from typing import Dict, Any

def randomize_choice_order(payload: Dict[str, Any]) -> Dict[str, Any]:
    choices = payload.get("choices", [])
    ids = [c.get("id") for c in choices]
    random.shuffle(ids)
    payload.setdefault("serve", {})["choice_order"] = ids
    return payload


def make_watermark(session_id: str) -> str:
    # lightweight per-serve watermark: session_id + timestamp bucket
    bucket = int(time.time() // 60)
    return f"{session_id}_{bucket}"
