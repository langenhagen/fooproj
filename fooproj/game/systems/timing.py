"""Shared timing helpers for per-frame gameplay systems."""

from typing import cast

import ursina


def get_frame_dt() -> float:
    """Read frame delta from Ursina's dynamic runtime module."""
    # Ursina exposes frame delta via dynamic module attributes.
    # B009: getattr-with-constant; ursina.time.dt is dynamic at runtime.
    return cast("float", getattr(getattr(ursina, "time"), "dt", 0.0))  # noqa: B009
