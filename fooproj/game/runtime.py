"""Ursina runtime bootstrap functions."""

from typing import TYPE_CHECKING, cast

import ursina
import ursina.color as color_module
from ursina import Entity, Sky, Text, Vec3, camera, mouse, scene, window
from ursina.main import Ursina

from .config import GameSettings
from .scene import EntityBlueprint, starter_scene_blueprints

if TYPE_CHECKING:
    from ursina.color import Color


def resolve_color(color_name: str) -> Color:
    """Resolve a color name from Ursina's built-in color palette."""
    return cast("Color", getattr(color_module, color_name, color_module.white))


def spawn_entity(blueprint: EntityBlueprint) -> None:
    """Spawn one entity from a scene blueprint."""
    Entity(
        model=blueprint.model,
        color=resolve_color(blueprint.color_name),
        scale=Vec3(blueprint.scale.x, blueprint.scale.y, blueprint.scale.z),
        position=Vec3(blueprint.position.x, blueprint.position.y, blueprint.position.z),
    )


def configure_window(settings: GameSettings) -> None:
    """Apply top-level window settings."""
    window.title = settings.window_title
    window.borderless = settings.borderless
    window.fullscreen = settings.fullscreen


def spawn_player() -> Entity:
    """Create a simple low-poly car as the controllable player entity."""
    car = Entity(position=Vec3(0.0, 0.35, 0.0))

    Entity(
        parent=car,
        model="cube",
        color=color_module.orange,
        scale=Vec3(1.8, 0.4, 3.2),
        position=Vec3(0.0, 0.0, 0.0),
    )
    Entity(
        parent=car,
        model="cube",
        color=color_module.azure,
        scale=Vec3(1.3, 0.45, 1.4),
        position=Vec3(0.0, 0.42, -0.2),
    )
    Entity(
        parent=car,
        model="cube",
        color=color_module.red,
        scale=Vec3(0.35, 0.2, 0.25),
        position=Vec3(0.0, 0.12, 1.55),
    )

    wheel_color = color_module.black
    wheel_scale = Vec3(0.42, 0.42, 0.42)
    for x_pos in (-0.85, 0.85):
        for z_pos in (-1.1, 1.1):
            Entity(
                parent=car,
                model="sphere",
                color=wheel_color,
                scale=wheel_scale,
                position=Vec3(x_pos, -0.18, z_pos),
            )

    return car


def configure_camera() -> None:
    """Set up the camera for third-person orbit controls."""
    camera.parent = scene
    camera.rotation = Vec3(0.0, 0.0, 0.0)


def create_camera_orbit_rig(settings: GameSettings) -> tuple[Entity, Entity]:
    """Create yaw/pitch pivots used for stable camera orbit."""
    yaw_pivot = Entity(parent=scene)
    pitch_pivot = Entity(parent=yaw_pivot)
    camera.parent = pitch_pivot
    camera.position = Vec3(0.0, 0.0, -settings.camera_distance)
    camera.rotation = Vec3(0.0, 0.0, 0.0)
    return yaw_pivot, pitch_pivot


def configure_mouse_capture() -> None:
    """Capture the mouse cursor for look controls."""
    mouse.locked = True
    mouse.visible = False


def create_controls_hint() -> None:
    """Render controls help text."""
    Text(
        text=(
            "Move: arrow keys (forward/back + strafe)\n"
            "Turn: page up/down + mouse (captured)"
        ),
        x=-0.86,
        y=0.47,
        scale=0.9,
        background=True,
    )


def install_movement_controller(
    player: Entity,
    yaw_pivot: Entity,
    pitch_pivot: Entity,
    settings: GameSettings,
) -> Entity:
    """Attach per-frame movement handling to a controller entity."""
    controller = Entity()
    yaw_angle = player.rotation_y
    pitch_angle = 18.0

    def controller_update() -> None:
        nonlocal yaw_angle
        nonlocal pitch_angle
        yaw_angle, pitch_angle = apply_player_input(
            player,
            yaw_pivot,
            pitch_pivot,
            settings,
            yaw_angle,
            pitch_angle,
        )

    controller.update = controller_update
    return controller


def apply_player_input(
    player: Entity,
    yaw_pivot: Entity,
    pitch_pivot: Entity,
    settings: GameSettings,
    yaw_angle: float,
    pitch_angle: float,
) -> tuple[float, float]:
    """Apply keyboard movement and rotation to the player."""
    held = cast("dict[str, float]", getattr(ursina, "held_keys", {}))
    forward_amount = held.get("up arrow", 0.0) - held.get("down arrow", 0.0)
    strafe_amount = held.get("right arrow", 0.0) - held.get("left arrow", 0.0)
    turn_amount = held.get("page down", 0.0) - held.get("page up", 0.0)
    mouse_velocity = cast("Vec3", getattr(mouse, "velocity", Vec3(0.0, 0.0, 0.0)))

    # Ursina exposes frame delta via dynamic module attributes.
    dt = cast("float", getattr(getattr(ursina, "time"), "dt", 0.0))  # noqa: B009  # B009: getattr-with-constant
    player.position += player.forward * (forward_amount * settings.move_speed * dt)
    player.position += player.right * (strafe_amount * settings.move_speed * dt)
    player.rotation_y += turn_amount * settings.turn_speed * dt

    yaw_angle += mouse_velocity.x * settings.mouse_look_speed

    pitch_angle += mouse_velocity.y * settings.mouse_look_speed
    pitch_angle = max(-70.0, min(70.0, pitch_angle))

    yaw_pivot.world_position = player.world_position + Vec3(
        0.0, settings.camera_height, 0.0
    )
    yaw_pivot.rotation = Vec3(0.0, yaw_angle, 0.0)
    pitch_pivot.rotation = Vec3(pitch_angle, 0.0, 0.0)
    camera.rotation_z = 0.0

    return yaw_angle, pitch_angle


def run_game(settings: GameSettings | None = None) -> None:
    """Run the Ursina starter sandbox."""
    active_settings = GameSettings() if settings is None else settings
    app = cast("object", Ursina(development_mode=active_settings.development_mode))

    configure_window(active_settings)

    for blueprint in starter_scene_blueprints():
        spawn_entity(blueprint)

    player = spawn_player()
    configure_camera()
    yaw_pivot, pitch_pivot = create_camera_orbit_rig(active_settings)
    configure_mouse_capture()
    create_controls_hint()
    install_movement_controller(player, yaw_pivot, pitch_pivot, active_settings)

    Sky()
    # Ursina's app proxy is typed as object here, so dynamic access is needed.
    run_callable = getattr(app, "run")  # noqa: B009  # B009: getattr-with-constant
    run_callable()
