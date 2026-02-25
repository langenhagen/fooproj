"""Shared timing helpers for per-frame gameplay systems."""

from contextlib import suppress
from math import isfinite

import ursina

MAX_FRAME_DT_SECONDS = 0.1


def clamp_frame_dt(frame_dt: float) -> float:
    """Clamp frame delta to a safe range for stable simulation steps."""
    if not isfinite(frame_dt):
        return 0.0
    if frame_dt <= 0.0:
        return 0.0
    return min(frame_dt, MAX_FRAME_DT_SECONDS)


def get_frame_dt() -> float:
    """Read frame delta from Ursina's dynamic runtime module."""
    # Ursina exposes frame delta via dynamic module attributes.
    time_module = getattr(ursina, "time", None)
    raw_dt = getattr(time_module, "dt", 0.0)
    with suppress(TypeError, ValueError):
        return clamp_frame_dt(float(raw_dt))
    return 0.0
