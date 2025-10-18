from __future__ import annotations

from typing import List, Optional
import os


def _normalize(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    v = value.strip()
    return v.lower() if v else None


def _next_type_in_order(types: List[str], current_norm: Optional[str]) -> Optional[str]:
    if not types:
        return None
    order = sorted(set(t for t in (_normalize(t) for t in types) if t))
    if not order:
        return None
    if current_norm not in order:
        return order[0]
    idx = order.index(current_norm)
    return order[(idx + 1) % len(order)]


def choose_next_type(
    *,
    available_types: List[str],
    last_type: Optional[str],
    serves_in_current_type: int,
) -> Optional[str]:
    """Dev-only policy stub.

    Default: continue with last_type (same-type).
    If ENGINE_STRICT=1 and serves_in_current_type >= POLICY_N (default 3), rotate to next type.
    Returns a normalized type string or None to indicate "no preference".
    """
    last_norm = _normalize(last_type)
    strict = (os.environ.get("ENGINE_STRICT", "").strip().lower() in ("1", "true", "yes", "on"))
    try:
        n = int(os.environ.get("POLICY_N", "3"))
    except ValueError:
        n = 3
    if n < 1:
        n = 3

    if strict and serves_in_current_type >= n:
        return _next_type_in_order(available_types, last_norm)
    return last_norm
