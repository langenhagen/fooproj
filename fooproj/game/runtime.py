"""Ursina runtime bootstrap functions."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import ursina
import ursina.color as color_module
import ursina.shaders as ursina_shaders
from ursina import (
    AmbientLight,
    DirectionalLight,
    Entity,
    Sky,
    Text,
    Vec3,
    camera,
    mouse,
    scene,
    window,
)
from ursina.main import Ursina

from .config import CameraSettings, GameSettings, MovementSettings
from .scene import EntityBlueprint, starter_scene_blueprints

if TYPE_CHECKING:
    from ursina.color import Color


LIT_SHADER = cast("object", ursina_shaders.lit_with_shadows_shader)


@dataclass(slots=True)
class OrbitControlState:
    """Mutable orbit camera state used across input frames."""

    yaw_angle: float
    pitch_angle: float
    camera_distance: float


@dataclass(frozen=True, slots=True)
class OrbitRig:
    """Holds yaw and pitch pivot entities for camera orbit."""

    yaw_pivot: Entity
    pitch_pivot: Entity


def resolve_color(color_name: str) -> Color:
    """Resolve a color name from Ursina's built-in color palette."""
    return cast("Color", getattr(color_module, color_name, color_module.white))


def spawn_entity(blueprint: EntityBlueprint) -> None:
    """Spawn one entity from a scene blueprint."""
    entity = Entity(
        model=blueprint.model,
        color=resolve_color(blueprint.color_name),
        scale=Vec3(blueprint.scale.x, blueprint.scale.y, blueprint.scale.z),
        position=Vec3(blueprint.position.x, blueprint.position.y, blueprint.position.z),
    )
    entity.shader = LIT_SHADER


def configure_window(settings: GameSettings) -> None:
    """Apply top-level window settings."""
    window.title = settings.window_title
    window.borderless = settings.borderless
    window.fullscreen = settings.fullscreen


def spawn_player() -> Entity:
    """Create a simple low-poly car as the controllable player entity."""
    car = Entity(position=Vec3(0.0, 0.35, 0.0))

    body = Entity(
        parent=car,
        model="cube",
        color=color_module.orange,
        scale=Vec3(1.8, 0.4, 3.2),
        position=Vec3(0.0, 0.0, 0.0),
    )
    body.shader = LIT_SHADER
    cabin = Entity(
        parent=car,
        model="cube",
        color=color_module.azure,
        scale=Vec3(1.3, 0.45, 1.4),
        position=Vec3(0.0, 0.42, -0.2),
    )
    cabin.shader = LIT_SHADER
    marker = Entity(
        parent=car,
        model="cube",
        color=color_module.red,
        scale=Vec3(0.35, 0.2, 0.25),
        position=Vec3(0.0, 0.12, 1.55),
    )
    marker.shader = LIT_SHADER

    wheel_color = color_module.black
    wheel_scale = Vec3(0.42, 0.42, 0.42)
    for x_pos in (-0.85, 0.85):
        for z_pos in (-1.1, 1.1):
            wheel = Entity(
                parent=car,
                model="sphere",
                color=wheel_color,
                scale=wheel_scale,
                position=Vec3(x_pos, -0.18, z_pos),
            )
            wheel.shader = LIT_SHADER

    return car


def configure_camera() -> None:
    """Set up the camera for third-person orbit controls."""
    camera.parent = scene
    camera.rotation = Vec3(0.0, 0.0, 0.0)


def create_camera_orbit_rig(settings: GameSettings) -> OrbitRig:
    """Create yaw/pitch pivots used for stable camera orbit."""
    yaw_pivot = Entity(parent=scene)
    pitch_pivot = Entity(parent=yaw_pivot)
    camera.parent = pitch_pivot
    camera.position = Vec3(0.0, 0.0, -settings.camera.distance)
    camera.rotation = Vec3(0.0, 0.0, 0.0)
    return OrbitRig(yaw_pivot=yaw_pivot, pitch_pivot=pitch_pivot)


def configure_mouse_capture() -> None:
    """Capture the mouse cursor for look controls."""
    mouse.locked = True
    mouse.visible = False


def create_controls_hint() -> None:
    """Render controls help text."""
    Text(
        text=(
            "Move: arrow keys (forward/back + strafe)\n"
            "Turn: page up/down + mouse (captured)\n"
            "Zoom: mouse wheel"
        ),
        x=-0.86,
        y=0.47,
        scale=0.9,
        background=True,
    )


def configure_lighting() -> None:
    """Create key/fill lights with shadows for better scene depth."""
    key_light = DirectionalLight(shadows=True)
    key_light.color = color_module.white
    key_light.look_at(Vec3(1.0, -1.0, -0.7))

    fill_light = DirectionalLight(shadows=False)
    fill_light.color = color_module.white33
    fill_light.look_at(Vec3(-0.6, -0.4, 0.8))

    ambient_light = AmbientLight()
    ambient_light.color = color_module.rgba(0.22, 0.24, 0.28, 1.0)


def compute_keyboard_axes(held: dict[str, float]) -> tuple[float, float, float]:
    """Compute movement axes from the current held-key mapping."""
    forward_amount = held.get("up arrow", 0.0) - held.get("down arrow", 0.0)
    strafe_amount = held.get("right arrow", 0.0) - held.get("left arrow", 0.0)
    turn_amount = held.get("page down", 0.0) - held.get("page up", 0.0)
    return forward_amount, strafe_amount, turn_amount


def compute_look_angles(
    yaw_angle: float,
    pitch_angle: float,
    mouse_velocity: Vec3,
    mouse_look_speed: float,
) -> tuple[float, float]:
    """Update yaw and pitch from mouse input and clamp pitch."""
    next_yaw = yaw_angle + (mouse_velocity.x * mouse_look_speed)
    next_pitch = pitch_angle + (mouse_velocity.y * mouse_look_speed)
    next_pitch = max(-90.0, min(90.0, next_pitch))
    return next_yaw, next_pitch


def compute_zoom_distance(
    current_distance: float,
    scroll_direction: int,
    min_distance: float,
    max_distance: float | None,
    zoom_step: float,
) -> float:
    """Adjust and clamp camera zoom distance from scroll input."""
    next_distance = current_distance - (scroll_direction * zoom_step)
    if max_distance is None:
        return max(min_distance, next_distance)

    return max(min_distance, min(max_distance, next_distance))


def install_movement_controller(
    player: Entity,
    orbit_rig: OrbitRig,
    settings: GameSettings,
) -> Entity:
    """Attach per-frame movement handling to a controller entity."""
    controller = Entity()
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
        if key == "scroll up":
            control_state.camera_distance = compute_zoom_distance(
                control_state.camera_distance,
                scroll_direction=1,
                min_distance=settings.camera.min_distance,
                max_distance=settings.camera.max_distance,
                zoom_step=settings.camera.zoom_step,
            )
        elif key == "scroll down":
            control_state.camera_distance = compute_zoom_distance(
                control_state.camera_distance,
                scroll_direction=-1,
                min_distance=settings.camera.min_distance,
                max_distance=settings.camera.max_distance,
                zoom_step=settings.camera.zoom_step,
            )

    controller.update = controller_update
    controller.input = controller_input
    return controller


def apply_player_input(
    player: Entity,
    orbit_rig: OrbitRig,
    movement_settings: MovementSettings,
    camera_settings: CameraSettings,
    control_state: OrbitControlState,
) -> None:
    """Apply keyboard movement and rotation to the player."""
    held = cast("dict[str, float]", getattr(ursina, "held_keys", {}))
    forward_amount, strafe_amount, turn_amount = compute_keyboard_axes(held)
    mouse_velocity = cast("Vec3", getattr(mouse, "velocity", Vec3(0.0, 0.0, 0.0)))

    # Ursina exposes frame delta via dynamic module attributes.
    # B009: getattr-with-constant; ursina.time.dt is dynamic at runtime.
    dt = cast("float", getattr(getattr(ursina, "time"), "dt", 0.0))  # noqa: B009
    player.position += player.forward * (
        forward_amount * movement_settings.move_speed * dt
    )
    player.position += player.right * (
        strafe_amount * movement_settings.move_speed * dt
    )
    player.rotation_y += turn_amount * movement_settings.turn_speed * dt

    control_state.yaw_angle, control_state.pitch_angle = compute_look_angles(
        control_state.yaw_angle,
        control_state.pitch_angle,
        mouse_velocity,
        camera_settings.mouse_look_speed,
    )

    orbit_rig.yaw_pivot.world_position = player.world_position + Vec3(
        0.0,
        camera_settings.height,
        0.0,
    )
    orbit_rig.yaw_pivot.rotation = Vec3(0.0, control_state.yaw_angle, 0.0)
    orbit_rig.pitch_pivot.rotation = Vec3(control_state.pitch_angle, 0.0, 0.0)
    camera.z = -control_state.camera_distance
    camera.rotation_z = 0.0


def run_game(settings: GameSettings | None = None) -> None:
    """Run the Ursina starter sandbox."""
    active_settings = GameSettings() if settings is None else settings
    app = cast("object", Ursina(development_mode=active_settings.development_mode))

    configure_window(active_settings)

    for blueprint in starter_scene_blueprints():
        spawn_entity(blueprint)

    player = spawn_player()
    configure_camera()
    orbit_rig = create_camera_orbit_rig(active_settings)
    configure_mouse_capture()
    create_controls_hint()
    configure_lighting()
    install_movement_controller(player, orbit_rig, active_settings)

    Sky()
    # Ursina's app proxy is typed as object here, so dynamic access is needed.
    run_callable = getattr(app, "run")  # noqa: B009  # B009: getattr-with-constant
    run_callable()
