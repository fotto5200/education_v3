import json
from pathlib import Path
from typing import Any, Dict

_mock_item_serve: Dict[str, Any] | None = None
_mock_submit_result: Dict[str, Any] | None = None

ROOT = Path(__file__).resolve().parents[2]


def load_mocks() -> None:
    global _mock_item_serve, _mock_submit_result
    item_path = ROOT / "mock_item_serve.json"
    result_path = ROOT / "mock_submit_result.json"
    if item_path.exists():
        _mock_item_serve = json.loads(item_path.read_text(encoding="utf-8"))
    if result_path.exists():
        _mock_submit_result = json.loads(result_path.read_text(encoding="utf-8"))


def get_mock_item_serve() -> Dict[str, Any]:
    if _mock_item_serve is None:
        return {
            "version": "1.0",
            "session_id": "s_anon",
            "item": {
                "id": "i_mock",
                "type": "mcq",
                "content": {"html": "Find \\(? m \\)? if \\(? y = mx + b \\)?"},
            },
            "choices": [
                {"id": "A", "text": "1"},
                {"id": "B", "text": "2"},
                {"id": "C", "text": "3"},
            ],
            "serve": {"seed": "seed", "choice_order": ["A", "B", "C"], "watermark": "demo"},
        }
    return json.loads(json.dumps(_mock_item_serve))


def get_mock_submit_result() -> Dict[str, Any]:
    if _mock_submit_result is None:
        return {"correct": True, "explanation": {"html": "Correct."}}
    return json.loads(json.dumps(_mock_submit_result))
