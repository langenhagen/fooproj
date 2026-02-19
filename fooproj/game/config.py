"""Runtime configuration for the Ursina sandbox."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameSettings:
    """Settings used to bootstrap the Ursina app."""

    window_title: str = "fooproj Ursina sandbox"
    borderless: bool = False
    fullscreen: bool = False
    development_mode: bool = True
