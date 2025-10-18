from __future__ import annotations

from collections import deque
from typing import Any, Deque, Dict, List, Optional
import os
import random
from . import selection_repo
from .policy_engine import choose_next_type


class _SessionState:
    def __init__(self, recent_window: int) -> None:
        self.recent_window: int = recent_window
        self.recent_ids: Deque[str] = deque(maxlen=recent_window)
        self.queue: List[Dict[str, Any]] = []  # queued canonical items for this session
        self.last_type: Optional[str] = None
        self.active_type: Optional[str] = None  # queue corresponds to this type (None = all)
        self.serves_in_current_type: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recent_window": self.recent_window,
            "recent_ids": list(self.recent_ids),
            "last_type": self.last_type,
            "active_type": self.active_type,
            "serves_in_current_type": self.serves_in_current_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "_SessionState":
        recent_window = int(data.get("recent_window", 5))
        s = cls(recent_window)
        for rid in data.get("recent_ids", []) or []:
            if isinstance(rid, str) and rid:
                s.recent_ids.append(rid)
        s.last_type = data.get("last_type")
        s.active_type = data.get("active_type")
        try:
            s.serves_in_current_type = int(data.get("serves_in_current_type", 0))
        except Exception:
            s.serves_in_current_type = 0
        return s


class SelectionManager:
    """In-memory, session-scoped selector with no immediate repeats and optional type scoping/policy.

    - Maintains a per-session recent window of served item ids (default 5).
    - Optionally scopes selection by item.type (override via query param or last served type).
    - Optional simple policy: rotate to next type after N serves.
    - Optional policy engine stub: when enabled, recommends next type; defaults to same-type.
    - Optional dev persistence: load/save state to a local JSON file when enabled.
    - Rebuilds queue when the active type changes or the queue empties.
    - If exclusion yields no candidates (e.g., too few items), clears recent and rebuilds.
    """

    def __init__(self, recent_window: int = 5) -> None:
        self._recent_window = recent_window
        self._by_session: Dict[str, _SessionState] = {}
        # Load persisted state if enabled
        if selection_repo.is_enabled():
            raw = selection_repo.load_selection_state()
            if isinstance(raw, dict):
                for sid, payload in raw.items():
                    try:
                        self._by_session[sid] = _SessionState.from_dict(payload)
                    except Exception:
                        continue

    def _save(self) -> None:
        if not selection_repo.is_enabled():
            return
        try:
            serializable = {sid: st.to_dict() for sid, st in self._by_session.items() if sid and sid != "s_anon"}
            selection_repo.save_selection_state(serializable)
        except Exception:
            pass

    def _get_state(self, session_id: str) -> _SessionState:
        state = self._by_session.get(session_id)
        if state is None:
            state = _SessionState(self._recent_window)
            self._by_session[session_id] = state
            self._save()
        return state

    @staticmethod
    def _normalize(value: Optional[str]) -> Optional[str]:
        if not isinstance(value, str):
            return None
        v = value.strip()
        return v.lower() if v else None

    def _get_policy(self, policy: Optional[str]) -> tuple[str | None, int]:
        p = (policy or os.environ.get("POLICY") or "").strip().lower() or None
        try:
            n = int(os.environ.get("POLICY_N", "3"))
        except ValueError:
            n = 3
        if n < 1:
            n = 3
        return p, n

    def _next_type_in_order(self, types: List[str], current_norm: Optional[str]) -> Optional[str]:
        if not types:
            return None
        order = sorted(set(t for t in (self._normalize(t) for t in types) if t))
        if not order:
            return None
        if current_norm not in order:
            return order[0]
        idx = order.index(current_norm)
        return order[(idx + 1) % len(order)]

    def next_canonical(
        self,
        session_id: str,
        canonicals: List[Dict[str, Any]],
        *,
        target_type: Optional[str] = None,
        policy: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        if not canonicals:
            return None
        state = self._get_state(session_id)

        policy_name, policy_n = self._get_policy(policy)

        # Policy engine can recommend a type (dev/test). Takes precedence over last_type, but not over explicit override.
        engine_enabled = policy_name == "engine"
        engine_reco: Optional[str] = None
        if engine_enabled:
            available_types = [c.get("type", "") for c in canonicals]
            engine_reco = choose_next_type(
                available_types=available_types,
                last_type=state.last_type,
                serves_in_current_type=state.serves_in_current_type,
            )

        # Determine desired type precedence:
        # 1) explicit override via query
        # 2) policy engine recommendation (if any)
        # 3) when simple policy is active, use any preselected active_type (next type)
        # 4) fall back to last_type
        if target_type is not None:
            desired_type_norm = self._normalize(target_type)
        elif engine_reco:
            desired_type_norm = self._normalize(engine_reco)
        elif policy_name == "simple" and state.active_type:
            desired_type_norm = state.active_type
        else:
            desired_type_norm = self._normalize(state.last_type)

        # If explicit override changes type, reset counter and force rebuild
        if target_type is not None:
            if self._normalize(target_type) != state.active_type:
                state.serves_in_current_type = 0
                state.active_type = None  # force rebuild for new type
                self._save()

        # Build candidate pool by type (if desired)
        if desired_type_norm:
            pool = [c for c in canonicals if self._normalize(c.get("type")) == desired_type_norm]
            if not pool:
                # Fallback to all items if requested type has no candidates
                pool = list(canonicals)
                desired_type_norm = None
        else:
            pool = list(canonicals)

        # Refill queue if empty or type changed
        if (not state.queue) or (state.active_type != desired_type_norm):
            recent = set(state.recent_ids)
            candidates = [c for c in pool if (c.get("id") or "") not in recent]
            if not candidates:
                # Too few items; allow repeats by clearing recent and using pool
                state.recent_ids.clear()
                candidates = list(pool)
            random.shuffle(candidates)
            state.queue = candidates
            state.active_type = desired_type_norm
            # When (re)building for a type, if that type matches last_type, keep counter; else reset
            if desired_type_norm != self._normalize(state.last_type):
                state.serves_in_current_type = 0
            self._save()

        # Pop next and record in recent
        chosen = state.queue.pop(0)
        item_id = chosen.get("id")
        if isinstance(item_id, str) and item_id:
            state.recent_ids.append(item_id)
        # Update last_type to the chosen item's type
        chosen_type = chosen.get("type")
        chosen_type_norm = self._normalize(chosen_type)
        if chosen_type_norm:
            # If we just served within the current active type, increment counter
            if state.active_type == chosen_type_norm:
                state.serves_in_current_type += 1
            else:
                state.serves_in_current_type = 1
            state.last_type = chosen_type
            self._save()

        # Simple policy: rotate type after N serves (only when no explicit type override present)
        if policy_name == "simple" and target_type is None and chosen_type_norm:
            if state.serves_in_current_type >= policy_n:
                # Determine next type and force next call to rebuild queue for it
                all_types = [c.get("type", "") for c in canonicals]
                next_type_norm = self._next_type_in_order(all_types, chosen_type_norm)
                state.active_type = next_type_norm
                state.serves_in_current_type = 0
                state.queue = []  # force rebuild on next call
                self._save()

        return chosen


# Singleton manager for app usage
selection_manager = SelectionManager(recent_window=5)
