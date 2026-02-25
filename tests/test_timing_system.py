"""Tests for runtime frame timing helpers."""

from __future__ import annotations

from math import inf, nan
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest import TestCase

from fooproj.game.systems import timing

if TYPE_CHECKING:
    import pytest


CHECKER = TestCase()


def test_clamp_frame_dt_bounds_values() -> None:
    """Clamp invalid and oversized frame deltas to safe values."""
    CHECKER.assertEqual(timing.clamp_frame_dt(-0.1), 0.0)
    CHECKER.assertEqual(timing.clamp_frame_dt(0.0), 0.0)
    CHECKER.assertEqual(timing.clamp_frame_dt(0.016), 0.016)
    CHECKER.assertEqual(timing.clamp_frame_dt(0.5), timing.MAX_FRAME_DT_SECONDS)


def test_clamp_frame_dt_rejects_non_finite_values() -> None:
    """Treat NaN and infinity as invalid frame timing."""
    CHECKER.assertEqual(timing.clamp_frame_dt(nan), 0.0)
    CHECKER.assertEqual(timing.clamp_frame_dt(inf), 0.0)


def test_get_frame_dt_reads_and_clamps_runtime_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read Ursina frame delta and apply clamping safeguards."""
    monkeypatch.setattr(timing.ursina, "time", SimpleNamespace(dt=0.75), raising=False)
    CHECKER.assertEqual(timing.get_frame_dt(), timing.MAX_FRAME_DT_SECONDS)


def test_get_frame_dt_handles_invalid_runtime_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fall back to zero when Ursina time exposes non-numeric dt."""
    monkeypatch.setattr(
        timing.ursina,
        "time",
        SimpleNamespace(dt="not-a-number"),
        raising=False,
    )
    CHECKER.assertEqual(timing.get_frame_dt(), 0.0)
