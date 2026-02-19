"""Tests for CLI helpers."""

from fooproj.cli import build_greeting


def test_build_greeting_default() -> None:
    """Return the default greeting when no name is given."""
    assert build_greeting() == "Hello from fooproj, world!"


def test_build_greeting_name() -> None:
    """Return a greeting containing the provided name."""
    assert build_greeting("Andreas") == "Hello from fooproj, Andreas!"
