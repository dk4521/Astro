import threading
import time

_lock = threading.Lock()
_crisis_sessions: dict[str, float] = {}

CRISIS_LOCK_TTL = 3600  # 1 hour

def mark_crisis(session_id: str) -> None:
    if not session_id:
        return
    with _lock:
        _crisis_sessions[session_id] = time.monotonic() + CRISIS_LOCK_TTL

def is_in_crisis(session_id: str) -> bool:
    if not session_id:
        return False
    with _lock:
        expires_at = _crisis_sessions.get(session_id)
        if expires_at is None:
            return False
        if time.monotonic() > expires_at:
            del _crisis_sessions[session_id]
            return False
        return True
