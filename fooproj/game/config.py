"""Runtime configuration for the Ursina sandbox."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MovementSettings:
    """Movement and rotation speeds for the player vehicle."""

    move_speed: float = 20.0
    turn_speed: float = 90.0


@dataclass(frozen=True, slots=True)
class CameraSettings:
    """Orbit camera settings for look and zoom behavior."""

    mouse_look_speed: float = 120.0
    distance: float = 10.0
    height: float = 1.1
    min_distance: float = 4.0
    max_distance: float | None = None
    zoom_step: float = 1.0
    chase_height_offset: float = 0.75
    chase_look_ahead: float = 3.6
    chase_follow_speed: float = 8.5


@dataclass(frozen=True, slots=True)
class CollisionSettings:
    """Collision and impact tuning for dynamic prop interactions."""

    impact_radius: float = 1.75
    rumble_cooldown_seconds: float = 0.12


@dataclass(frozen=True, slots=True)
class ShadowSettings:
    """Shadow and lighting tuning values for runtime visuals."""

    sun_direction: tuple[float, float, float] = (0.8, -1.2, -0.5)
    shadow_map_resolution: int = 4096
    ambient_rgba: tuple[float, float, float, float] = (0.22, 0.24, 0.28, 1.0)
    blur: float = 0.0008
    bias: float = 0.0005
    samples: int = 3
    bounds_scale: tuple[float, float, float] = (38.0, 20.0, 38.0)


@dataclass(frozen=True, slots=True)
class RivalSettings:
    """AI traffic/rival settings for looped track opponents."""

    enabled: bool = True
    count: int = 5
    min_speed: float = 11.0
    max_speed: float = 17.0
    lane_offsets: tuple[float, ...] = (-2.6, 0.0, 2.6)
    bob_amplitude: float = 0.06
    bob_speed: float = 2.4
    lane_rejoin_rate: float = 7.0


@dataclass(frozen=True, slots=True)
class GameSettings:
    """Settings used to bootstrap the Ursina app."""

    window_title: str = "fooproj"
    borderless: bool = False
    fullscreen: bool = False
    development_mode: bool = True
    movement: MovementSettings = field(default_factory=MovementSettings)
    camera: CameraSettings = field(default_factory=CameraSettings)
    collision: CollisionSettings = field(default_factory=CollisionSettings)
    shadow: ShadowSettings = field(default_factory=ShadowSettings)
    rivals: RivalSettings = field(default_factory=RivalSettings)
