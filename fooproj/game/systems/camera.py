"""Camera rig state and update helpers for orbit and chase modes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ursina import Entity, Vec3, camera, lerp_exponential_decay, scene

if TYPE_CHECKING:
    from fooproj.game.config import CameraSettings, GameSettings


@dataclass(slots=True)
class OrbitControlState:
    """Mutable orbit/chase camera state used across input frames."""

    yaw_angle: float
    pitch_angle: float
    camera_distance: float
    chase_camera_enabled: bool = False
    forward_speed: float = 0.0


@dataclass(frozen=True, slots=True)
class OrbitRig:
    """Holds yaw and pitch pivot entities for camera orbit."""

    yaw_pivot: Entity
    pitch_pivot: Entity


def configure_camera() -> None:
    """Set up the camera for third-person orbit controls."""
    camera.parent = scene
    camera.rotation = Vec3(0.0, 0.0, 0.0)


def create_camera_orbit_rig(settings: GameSettings) -> OrbitRig:
    """Create yaw and pitch pivots used for stable camera orbit."""
    yaw_pivot = Entity(name="camera_yaw_pivot", parent=scene)
    pitch_pivot = Entity(name="camera_pitch_pivot", parent=yaw_pivot)
    camera.parent = pitch_pivot
    camera.position = Vec3(0.0, 0.0, -settings.camera.distance)
    camera.rotation = Vec3(0.0, 0.0, 0.0)
    return OrbitRig(yaw_pivot=yaw_pivot, pitch_pivot=pitch_pivot)


def set_camera_mode(
    orbit_rig: OrbitRig,
    control_state: OrbitControlState,
    *,
    chase_camera_enabled: bool,
) -> None:
    """Switch camera mode and update camera parent state."""
    control_state.chase_camera_enabled = chase_camera_enabled
    if control_state.chase_camera_enabled:
        camera.parent = scene
        return

    camera.parent = orbit_rig.pitch_pivot
    camera.position = Vec3(0.0, 0.0, -control_state.camera_distance)
    camera.rotation = Vec3(0.0, 0.0, 0.0)


def compute_look_angles(
    yaw_angle: float,
    pitch_angle: float,
    look_velocity: Vec3,
    mouse_look_speed: float,
) -> tuple[float, float]:
    """Update yaw and pitch from look input and clamp pitch."""
    next_yaw = yaw_angle + (look_velocity.x * mouse_look_speed)
    next_pitch = pitch_angle + (look_velocity.y * mouse_look_speed)
    next_pitch = max(-90.0, min(90.0, next_pitch))
    return next_yaw, next_pitch


def compute_zoom_distance(
    current_distance: float,
    scroll_direction: int,
    min_distance: float,
    max_distance: float | None,
    zoom_step: float,
) -> float:
    """Adjust and clamp camera zoom distance from scroll-like input."""
    next_distance = current_distance - (scroll_direction * zoom_step)
    if max_distance is None:
        return max(min_distance, next_distance)

    return max(min_distance, min(max_distance, next_distance))


def update_chase_camera(
    player: Entity,
    camera_settings: CameraSettings,
    control_state: OrbitControlState,
    dt: float,
) -> None:
    """Update chase-camera position and look target."""
    target_position = (
        player.world_position
        - (player.forward * control_state.camera_distance)
        + Vec3(0.0, camera_settings.height + camera_settings.chase_height_offset, 0.0)
    )
    camera.world_position = cast(
        "Vec3",
        lerp_exponential_decay(
            camera.world_position,
            target_position,
            dt * camera_settings.chase_follow_speed,
        ),
    )
    camera.look_at(
        player.world_position
        + (player.forward * camera_settings.chase_look_ahead)
        + Vec3(0.0, camera_settings.height * 0.5, 0.0),
    )
    camera.rotation_z = 0.0


def update_orbit_camera(
    player: Entity,
    orbit_rig: OrbitRig,
    camera_settings: CameraSettings,
    control_state: OrbitControlState,
    look_velocity: Vec3,
) -> None:
    """Update orbit-camera pivots and zoom state from look input."""
    control_state.yaw_angle, control_state.pitch_angle = compute_look_angles(
        control_state.yaw_angle,
        control_state.pitch_angle,
        look_velocity,
        camera_settings.mouse_look_speed,
    )

    orbit_rig.yaw_pivot.world_position = player.world_position + Vec3(
        0.0,
        camera_settings.height,
        0.0,
    )
    orbit_rig.yaw_pivot.rotation = Vec3(0.0, control_state.yaw_angle, 0.0)
    orbit_rig.pitch_pivot.rotation = Vec3(control_state.pitch_angle, 0.0, 0.0)
    camera.position = Vec3(0.0, 0.0, -control_state.camera_distance)
    camera.rotation_z = 0.0
