"""
DARKWIN — Realtime Progress Hub
Thread-safe, UI-agnostic progress reporting for long-running pipelines.

Pipelines call :func:`advance` / :func:`set_pct` to move a global 0-100
pointer forward. The dashboard backend subscribes a listener which forwards
those updates over Socket.IO so progress bars update in real time.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

_pointer: float = 0.0
_pointer_lock = threading.Lock()

_listeners: list[Callable[[int, Optional[str]], None]] = []
_listeners_lock = threading.Lock()


def reset() -> None:
    """Return the progress pointer to 0 without notifying listeners."""
    global _pointer
    with _pointer_lock:
        _pointer = 0.0


def current() -> int:
    """Return the current progress as an integer percent (0-100)."""
    with _pointer_lock:
        return int(_pointer)


def subscribe(listener: Callable[[int, Optional[str]], None]) -> None:
    """Register a listener called as fn(progress_pct, message)."""
    with _listeners_lock:
        _listeners.append(listener)


def unsubscribe(listener: Callable[[int, Optional[str]], None]) -> None:
    """Remove a previously registered listener."""
    with _listeners_lock:
        try:
            _listeners.remove(listener)
        except ValueError:
            pass


def clear_listeners() -> None:
    """Remove all listeners (used on app lifecycle / tests)."""
    global _listeners
    with _listeners_lock:
        _listeners = []


def advance(delta: float, message: Optional[str] = None) -> None:
    """Move the progress pointer forward by `delta` (capped at 100) and
    notify listeners. This is the main realtime update entry point."""
    global _pointer
    with _pointer_lock:
        _pointer = min(100.0, max(0.0, _pointer + delta))
        pct = int(_pointer)
    _publish(pct, message)


def set_pct(pct: float, message: Optional[str] = None) -> None:
    """Jump the progress pointer to the given percent and notify listeners."""
    global _pointer
    with _pointer_lock:
        _pointer = min(100.0, max(0.0, float(pct)))
        value = int(_pointer)
    _publish(value, message)


def stage(label: str, weight: float, logger: Optional[Callable[..., None]] = None) -> None:
    """
    Convenience helper: mark that a stage is starting.

    Logs `label` (if a logger callable is given) and advances progress by
    `weight` so the dashboard can reflect the new phase immediately.
    """
    if logger:
        logger(label)
    advance(weight, label)


def _publish(pct: int, message: Optional[str]) -> None:
    with _listeners_lock:
        snapshot = list(_listeners)
    for listener in snapshot:
        try:
            listener(pct, message)
        except Exception:
            pass