"""Tests for collision-side safety and rumble helpers."""

from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest import TestCase

from fooproj.game.systems import collision

if TYPE_CHECKING:
    import pytest


CHECKER = TestCase()


def reset_rumble_cache() -> None:
    """Reset module-level rumble cache between tests."""
    collision.get_gamepad_vibrate.cache_clear()


def test_get_gamepad_vibrate_handles_missing_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return no rumble callable when gamepad module is unavailable."""
    reset_rumble_cache()

    def fake_import_module(name: str) -> object:
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(collision.importlib, "import_module", fake_import_module)
    CHECKER.assertIsNone(collision.get_gamepad_vibrate())


def test_get_gamepad_vibrate_caches_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve vibrate callable once and reuse it."""
    reset_rumble_cache()
    import_calls = 0

    def fake_vibrate(*_: object, **__: object) -> None:
        return

    def fake_import_module(name: str) -> object:
        nonlocal import_calls
        import_calls += 1
        CHECKER.assertEqual(name, "ursina.gamepad")
        return SimpleNamespace(vibrate=fake_vibrate)

    monkeypatch.setattr(collision.importlib, "import_module", fake_import_module)

    first = collision.get_gamepad_vibrate()
    second = collision.get_gamepad_vibrate()

    CHECKER.assertIs(first, fake_vibrate)
    CHECKER.assertIs(second, fake_vibrate)
    CHECKER.assertEqual(import_calls, 1)


def test_trigger_impact_rumble_ignores_low_speed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip rumble calls when impact speed is below threshold."""
    reset_rumble_cache()
    calls: list[object] = []

    def fake_vibrate(*_: object, **__: object) -> None:
        calls.append("called")

    def fake_get_gamepad_vibrate() -> object:
        return fake_vibrate

    monkeypatch.setattr(collision, "get_gamepad_vibrate", fake_get_gamepad_vibrate)

    collision.trigger_impact_rumble(collision.MIN_IMPACT_SPEED)
    CHECKER.assertEqual(calls, [])


def test_trigger_impact_rumble_swallows_runtime_driver_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Treat transient gamepad API failures as non-fatal."""
    reset_rumble_cache()

    def fake_vibrate(*_: object, **__: object) -> None:
        message = "device unavailable"
        raise RuntimeError(message)

    monkeypatch.setattr(collision, "get_gamepad_vibrate", lambda: fake_vibrate)

    collision.trigger_impact_rumble(5.0)
