"""Tests for CLI helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fooproj import cli

if TYPE_CHECKING:
    import pytest


def test_main_calls_run_game(monkeypatch: pytest.MonkeyPatch) -> None:
    """Launch the game runtime from the CLI entrypoint."""
    calls: list[str] = []

    def fake_run_game() -> None:
        calls.append("run")

    monkeypatch.setattr("fooproj.game.run_game", fake_run_game)
    cli.main()

    assert calls == ["run"]
