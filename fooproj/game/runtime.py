"""Ursina runtime bootstrap and gameplay system wiring."""

from pathlib import Path
from typing import cast

import ursina
from ursina import Entity, Sky, Text, Vec3, application, mouse, window
from ursina.main import Ursina

from .config import CameraSettings, GameSettings, MovementSettings
from .systems.camera import (
    OrbitControlState,
    OrbitRig,
    compute_zoom_distance,
    configure_camera,
    create_camera_orbit_rig,
    set_camera_mode,
    update_chase_camera,
    update_orbit_camera,
)
from .systems.collision import install_prop_physics_controller
from .systems.input import compute_control_axes
from .systems.movement import (
    FORWARD_MAX_SPEED_MULTIPLIER,
    compute_smoothed_forward_speed,
)
from .systems.spawn import spawn_player, spawn_world_entities
from .systems.timing import get_frame_dt
from .systems.visuals import configure_lighting
from .ui import create_controls_hint

SCROLL_DIRECTION_BY_KEY = {
    "scroll up": 1,
    "scroll down": -1,
    "gamepad dpad up": 1,
    "gamepad dpad down": -1,
}
CAMERA_TOGGLE_KEYS = {"c", "gamepad dpad left"}


def configure_window(settings: GameSettings) -> None:
    """Apply top-level window settings."""
    window.title = settings.window_title
    window.borderless = settings.borderless
    window.fullscreen = settings.fullscreen


def configure_mouse_capture() -> None:
    """Capture the mouse cursor for look controls."""
    mouse.locked = True
    mouse.visible = False


def apply_player_input(
    player: Entity,
    orbit_rig: OrbitRig,
    movement_settings: MovementSettings,
    camera_settings: CameraSettings,
    control_state: OrbitControlState,
) -> None:
    """Apply keyboard/gamepad movement and camera look updates."""
    held = cast("dict[str, float]", getattr(ursina, "held_keys", {}))
    mouse_velocity = cast("Vec3", getattr(mouse, "velocity", Vec3(0.0, 0.0, 0.0)))
    forward_amount, strafe_amount, turn_amount, look_velocity = compute_control_axes(
        held,
        mouse_velocity,
    )

    dt = get_frame_dt()
    max_forward_speed = movement_settings.move_speed * FORWARD_MAX_SPEED_MULTIPLIER
    control_state.forward_speed = compute_smoothed_forward_speed(
        control_state.forward_speed,
        forward_amount,
        max_forward_speed,
        dt,
    )
    player.position += player.forward * (control_state.forward_speed * dt)
    player.position += player.right * (
        strafe_amount * movement_settings.move_speed * dt
    )
    player.rotation_y += turn_amount * movement_settings.turn_speed * dt

    if control_state.chase_camera_enabled:
        update_chase_camera(
            player,
            camera_settings,
            control_state,
            dt,
        )
    else:
        update_orbit_camera(
            player,
            orbit_rig,
            camera_settings,
            control_state,
            look_velocity,
        )


def install_movement_controller(
    player: Entity,
    orbit_rig: OrbitRig,
    settings: GameSettings,
    controls_hint: Text,
) -> Entity:
    """Attach per-frame movement handling to a controller entity."""
    controller = Entity(name="player_input_controller")
    control_state = OrbitControlState(
        yaw_angle=player.rotation_y,
        pitch_angle=18.0,
        camera_distance=settings.camera.distance,
    )

    def controller_update() -> None:
        apply_player_input(
            player,
            orbit_rig,
            settings.movement,
            settings.camera,
            control_state,
        )

    def controller_input(key: str) -> None:
        if key == "escape":
            application.quit()

        if key == "u":
            controls_hint.enabled = not controls_hint.enabled

        if key in CAMERA_TOGGLE_KEYS:
            set_camera_mode(
                orbit_rig,
                control_state,
                chase_camera_enabled=not control_state.chase_camera_enabled,
            )

        scroll_direction = SCROLL_DIRECTION_BY_KEY.get(key)
        if scroll_direction is None:
            return

        control_state.camera_distance = compute_zoom_distance(
            control_state.camera_distance,
            scroll_direction=scroll_direction,
            min_distance=settings.camera.min_distance,
            max_distance=settings.camera.max_distance,
            zoom_step=settings.camera.zoom_step,
        )

    controller.update = controller_update
    controller.input = controller_input
    return controller


def run_game(settings: GameSettings | None = None) -> None:
    """Run the Ursina starter sandbox."""
    active_settings = GameSettings() if settings is None else settings
    app = cast("object", Ursina(development_mode=active_settings.development_mode))
    application.asset_folder = Path(__file__).resolve().parents[2]

    configure_window(active_settings)

    dynamic_props = spawn_world_entities()

    player = spawn_player()
    configure_camera()
    orbit_rig = create_camera_orbit_rig(active_settings)
    configure_mouse_capture()
    controls_hint = create_controls_hint()
    configure_lighting(player, active_settings.shadow)
    install_movement_controller(player, orbit_rig, active_settings, controls_hint)
    install_prop_physics_controller(player, dynamic_props, active_settings.collision)

    Sky()
    # Ursina's app proxy is typed as object here, so dynamic access is needed.
    run_callable = getattr(app, "run")  # noqa: B009  # B009: getattr-with-constant
    run_callable()
