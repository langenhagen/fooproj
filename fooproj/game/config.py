"""Runtime configuration for the Ursina sandbox."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameSettings:
    """Settings used to bootstrap the Ursina app."""

    window_title: str = "fooproj Ursina sandbox"
    borderless: bool = False
    fullscreen: bool = False
    development_mode: bool = True
    move_speed: float = 5.0
    turn_speed: float = 90.0
    mouse_look_speed: float = 120.0
    camera_distance: float = 10.0
    camera_height: float = 1.1
