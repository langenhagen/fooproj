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
CAR_IMPACT_RADIUS = 1.75


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


@dataclass(slots=True)
class DynamicProp:
    """Simple dynamic prop state for lightweight physics interactions."""

    entity: Entity
    velocity: Vec3
    radius: float
    mass: float


def resolve_color(color_name: str) -> Color:
    """Resolve a color name from Ursina's built-in color palette."""
    return cast("Color", getattr(color_module, color_name, color_module.white))


def spawn_entity(blueprint: EntityBlueprint) -> Entity:
    """Spawn one entity from a scene blueprint and return it."""
    entity = Entity(
        model=blueprint.model,
        color=resolve_color(blueprint.color_name),
        scale=Vec3(blueprint.scale.x, blueprint.scale.y, blueprint.scale.z),
        position=Vec3(blueprint.position.x, blueprint.position.y, blueprint.position.z),
    )
    entity.shader = LIT_SHADER
    return entity


def configure_window(settings: GameSettings) -> None:
    """Apply top-level window settings."""
    window.title = settings.window_title
    window.borderless = settings.borderless
    window.fullscreen = settings.fullscreen


def add_car_part(
    parent: Entity,
    model: str,
    color_value: Color,
    scale: Vec3,
    position: Vec3,
    rotation: Vec3 | None = None,
) -> Entity:
    """Create one shaded part for the player car prefab."""
    part = Entity(
        parent=parent,
        model=model,
        color=color_value,
        scale=scale,
        position=position,
    )
    if rotation is not None:
        part.rotation = rotation
    part.shader = LIT_SHADER
    return part


def spawn_player() -> Entity:
    """Create a richer low-poly sports car as the player entity."""
    car = Entity(position=Vec3(0.0, 0.48, 0.0))

    # Car body: base shell, mid shell, nose, rear deck.
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.3, 0.46, 4.6),
        position=Vec3(0.0, -0.02, 0.0),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.18, 0.44, 3.55),
        position=Vec3(0.0, 0.33, -0.02),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.1, 0.36, 1.65),
        position=Vec3(0.0, 0.31, 1.55),
        rotation=Vec3(2.0, 0.0, 0.0),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.02, 0.32, 1.2),
        position=Vec3(0.0, 0.31, -1.8),
        rotation=Vec3(-2.0, 0.0, 0.0),
    )

    # Cabin and glass.
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.azure,
        scale=Vec3(1.7, 0.42, 2.2),
        position=Vec3(0.0, 0.68, -0.28),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.azure,
        scale=Vec3(1.35, 0.2, 1.45),
        position=Vec3(0.0, 0.95, -0.28),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.light_gray,
        scale=Vec3(1.26, 0.18, 0.08),
        position=Vec3(0.0, 0.83, 0.58),
        rotation=Vec3(32.0, 0.0, 0.0),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.light_gray,
        scale=Vec3(1.16, 0.17, 0.08),
        position=Vec3(0.0, 0.81, -1.02),
        rotation=Vec3(-30.0, 0.0, 0.0),
    )

    # Bumpers.
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.dark_gray,
        scale=Vec3(2.22, 0.18, 0.34),
        position=Vec3(0.0, -0.03, 2.28),
    )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.dark_gray,
        scale=Vec3(2.14, 0.18, 0.34),
        position=Vec3(0.0, -0.03, -2.28),
    )

    # Side skirts.
    for x_pos in (-1.04, 1.04):
        add_car_part(
            parent=car,
            model="cube",
            color_value=color_module.dark_gray,
            scale=Vec3(0.11, 0.19, 2.85),
            position=Vec3(x_pos, -0.03, 0.02),
        )

    # Front headlights and rear lights.
    for x_pos in (-0.72, 0.72):
        add_car_part(
            parent=car,
            model="sphere",
            color_value=color_module.yellow,
            scale=Vec3(0.24, 0.24, 0.24),
            position=Vec3(x_pos, 0.15, 2.24),
        )
        add_car_part(
            parent=car,
            model="sphere",
            color_value=color_module.red,
            scale=Vec3(0.22, 0.22, 0.22),
            position=Vec3(x_pos, 0.18, -2.23),
        )

    # Mirrors.
    for x_pos in (-1.05, 1.05):
        add_car_part(
            parent=car,
            model="cube",
            color_value=color_module.gray,
            scale=Vec3(0.09, 0.18, 0.09),
            position=Vec3(x_pos, 0.61, 0.46),
        )
        add_car_part(
            parent=car,
            model="cube",
            color_value=color_module.light_gray,
            scale=Vec3(0.16, 0.07, 0.2),
            position=Vec3(x_pos * 1.02, 0.67, 0.46),
        )

    # Rear spoiler.
    for x_pos in (-0.56, 0.56):
        add_car_part(
            parent=car,
            model="cube",
            color_value=color_module.dark_gray,
            scale=Vec3(0.12, 0.32, 0.12),
            position=Vec3(x_pos, 0.62, -1.96),
        )
    add_car_part(
        parent=car,
        model="cube",
        color_value=color_module.dark_gray,
        scale=Vec3(1.42, 0.08, 0.28),
        position=Vec3(0.0, 0.74, -1.96),
    )

    # Wheels, hubs, and wheel bars.
    wheel_offsets = ((-1.12, 1.55), (1.12, 1.55), (-1.12, -1.55), (1.12, -1.55))
    for x_pos, z_pos in wheel_offsets:
        add_car_part(
            parent=car,
            model="sphere",
            color_value=color_module.black,
            scale=Vec3(0.62, 0.62, 0.62),
            position=Vec3(x_pos, -0.22, z_pos),
        )
        add_car_part(
            parent=car,
            model="sphere",
            color_value=color_module.light_gray,
            scale=Vec3(0.28, 0.28, 0.28),
            position=Vec3(x_pos, -0.22, z_pos),
        )
        add_car_part(
            parent=car,
            model="cube",
            color_value=color_module.dark_gray,
            scale=Vec3(0.72, 0.12, 0.16),
            position=Vec3(x_pos, -0.22, z_pos),
        )

    return car


def compute_prop_mass(scale: Vec3) -> float:
    """Approximate prop mass from visual volume."""
    volume = max(0.1, float(scale.x) * float(scale.y) * float(scale.z))
    return max(0.6, volume)


def blueprint_to_dynamic_prop(
    entity: Entity, blueprint: EntityBlueprint
) -> DynamicProp:
    """Create dynamic-physics state for a spawned scene entity."""
    scale = Vec3(blueprint.scale.x, blueprint.scale.y, blueprint.scale.z)
    radius = max(scale.x, scale.z) * 0.5
    return DynamicProp(
        entity=entity,
        velocity=Vec3(0.0, 0.0, 0.0),
        radius=radius,
        mass=compute_prop_mass(scale),
    )


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


def compute_player_velocity(
    current_position: Vec3, previous_position: Vec3, dt: float
) -> Vec3:
    """Compute frame velocity from two positions and a delta time."""
    if dt <= 0.0:
        return Vec3(0.0, 0.0, 0.0)

    inverse_dt = 1.0 / dt
    return Vec3(
        (current_position.x - previous_position.x) * inverse_dt,
        (current_position.y - previous_position.y) * inverse_dt,
        (current_position.z - previous_position.z) * inverse_dt,
    )


def resolve_ground_contact(
    position_y: float,
    velocity_y: float,
    radius: float,
) -> tuple[float, float]:
    """Clamp a prop above ground and bounce vertical velocity."""
    if position_y >= radius:
        return position_y, velocity_y

    next_y = radius
    next_velocity_y = velocity_y
    if velocity_y < 0.0:
        next_velocity_y = -velocity_y * 0.35
        if abs(next_velocity_y) < 0.25:
            next_velocity_y = 0.0

    return next_y, next_velocity_y


def install_prop_physics_controller(player: Entity, props: list[DynamicProp]) -> Entity:
    """Attach simple prop physics and player impact responses."""
    controller = Entity()
    previous_player_position = Vec3(player.position)

    def controller_update() -> None:
        nonlocal previous_player_position

        dt = cast("float", getattr(getattr(ursina, "time"), "dt", 0.0))  # noqa: B009  # B009: getattr-with-constant
        player_velocity = compute_player_velocity(
            player.position, previous_player_position, dt
        )
        previous_player_position = Vec3(player.position)

        for prop in props:
            prop.velocity.y -= 9.81 * dt

            to_prop = prop.entity.position - player.position
            distance = to_prop.length()
            impact_radius = CAR_IMPACT_RADIUS + prop.radius
            player_speed = player_velocity.length()
            if distance < impact_radius and player_speed > 0.1:
                push_dir = to_prop.normalized() if distance > 0.0001 else player.forward
                penetration = impact_radius - distance
                if penetration > 0.0:
                    prop.entity.position += push_dir * (penetration * 0.4)
                prop.velocity += push_dir * (player_speed * (0.8 / prop.mass))
                prop.velocity.y = max(prop.velocity.y, 1.6)

            prop.entity.position += prop.velocity * dt

            next_y, next_velocity_y = resolve_ground_contact(
                prop.entity.y,
                prop.velocity.y,
                prop.radius,
            )
            prop.entity.y = next_y
            prop.velocity.y = next_velocity_y
            if next_y <= prop.radius + 0.001:
                prop.velocity.x *= 0.97
                prop.velocity.z *= 0.97

    controller.update = controller_update
    return controller


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

    dynamic_props: list[DynamicProp] = []
    for blueprint in starter_scene_blueprints():
        entity = spawn_entity(blueprint)
        if blueprint.model != "plane":
            dynamic_props.append(blueprint_to_dynamic_prop(entity, blueprint))

    player = spawn_player()
    configure_camera()
    orbit_rig = create_camera_orbit_rig(active_settings)
    configure_mouse_capture()
    create_controls_hint()
    configure_lighting()
    install_movement_controller(player, orbit_rig, active_settings)
    install_prop_physics_controller(player, dynamic_props)

    Sky()
    # Ursina's app proxy is typed as object here, so dynamic access is needed.
    run_callable = getattr(app, "run")  # noqa: B009  # B009: getattr-with-constant
    run_callable()
