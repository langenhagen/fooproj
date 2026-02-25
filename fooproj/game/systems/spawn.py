"""Entity spawn/despawn orchestration around scene blueprints."""

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import ursina.color as color_module
import ursina.shaders as ursina_shaders
from ursina import Entity, Vec3, application

from fooproj.game.scene import EntityBlueprint, starter_scene_blueprints

if TYPE_CHECKING:
    from ursina.color import Color


LIT_SHADER = cast("object", ursina_shaders.lit_with_shadows_shader)
CAR_MODEL_FILE = (
    Path(__file__).resolve().parents[3] / "assets" / "De_Tomaso_P72_2020.obj"
)
CAR_BASE_TEXTURE_FILE = (
    Path(__file__).resolve().parents[3]
    / "assets"
    / "De_Tomaso_Textures"
    / "Detomasop72_Base_Color.png"
)
CAR_BASE_TEXTURE_PATH = "assets/De_Tomaso_Textures/Detomasop72_Base_Color.png"
CAR_TARGET_LENGTH = 4.8


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


def mark_lit_shadowed(entity: Entity) -> Entity:
    """Apply the project-default lit shader and shadow camera mask."""
    entity.shader = LIT_SHADER
    entity.show(0b0001)
    return entity


def spawn_entity(blueprint: EntityBlueprint) -> Entity:
    """Spawn one entity from a scene blueprint and return it."""
    # Stable names make runtime inspection in Ursina's entity list easier.
    entity_name = (
        f"world_{blueprint.model}_"
        f"{round(blueprint.position.x)}_"
        f"{round(blueprint.position.z)}"
    )
    entity = Entity(
        name=entity_name,
        model=blueprint.model,
        color=resolve_color(blueprint.color_name),
        scale=Vec3(blueprint.scale.x, blueprint.scale.y, blueprint.scale.z),
        position=Vec3(blueprint.position.x, blueprint.position.y, blueprint.position.z),
    )
    return mark_lit_shadowed(entity)


def compute_prop_mass(scale: Vec3) -> float:
    """Approximate prop mass from visual volume."""
    volume = max(0.1, float(scale.x) * float(scale.y) * float(scale.z))
    return max(0.6, volume)


def blueprint_to_dynamic_prop(
    entity: Entity,
    blueprint: EntityBlueprint,
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


def spawn_world_entities() -> list[DynamicProp]:
    """Spawn static scene entities and return dynamic-physics props."""
    dynamic_props: list[DynamicProp] = []
    for blueprint in starter_scene_blueprints():
        entity = spawn_entity(blueprint)
        if blueprint.is_dynamic:
            dynamic_props.append(blueprint_to_dynamic_prop(entity, blueprint))
    return dynamic_props


def side_label(x_pos: float) -> str:
    """Return stable left/right labels from signed x positions."""
    return "left" if x_pos < 0.0 else "right"


def wheel_label(x_pos: float, z_pos: float) -> str:
    """Return stable wheel labels from wheel-local positions."""
    axle_label = "front" if z_pos > 0.0 else "rear"
    return f"{axle_label}_{side_label(x_pos)}"


# PLR0913 / pylint R0913,R0917: explicit geometry parameters keep
# primitive car part callsites readable and easy to tweak.
# pylint: disable=too-many-arguments,too-many-positional-arguments
def add_car_part(  # noqa: PLR0913
    parent: Entity,
    name: str,
    model: str,
    color_value: Color,
    scale: Vec3,
    position: Vec3,
    rotation: Vec3 | None = None,
) -> Entity:
    """Create one shaded part for the player car prefab."""
    part = Entity(
        parent=parent,
        name=name,
        model=model,
        color=color_value,
        scale=scale,
        position=position,
    )
    if rotation is not None:
        part.rotation = rotation
    return mark_lit_shadowed(part)


# pylint: enable=too-many-arguments,too-many-positional-arguments


def spawn_primitive_player() -> Entity:
    """Create a richer low-poly sports car as the player entity."""
    car = Entity(name="player_car_primitive_root", position=Vec3(0.0, 0.48, 0.0))

    # Car body: base shell, mid shell, nose, rear deck.
    add_car_part(
        parent=car,
        name="car_body_base",
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.3, 0.46, 4.6),
        position=Vec3(0.0, -0.02, 0.0),
    )
    add_car_part(
        parent=car,
        name="car_body_mid",
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.18, 0.44, 3.55),
        position=Vec3(0.0, 0.33, -0.02),
    )
    add_car_part(
        parent=car,
        name="car_body_nose",
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.1, 0.36, 1.65),
        position=Vec3(0.0, 0.31, 1.55),
        rotation=Vec3(2.0, 0.0, 0.0),
    )
    add_car_part(
        parent=car,
        name="car_body_rear",
        model="cube",
        color_value=color_module.orange,
        scale=Vec3(2.02, 0.32, 1.2),
        position=Vec3(0.0, 0.31, -1.8),
        rotation=Vec3(-2.0, 0.0, 0.0),
    )

    # Cabin and glass.
    add_car_part(
        parent=car,
        name="car_cabin_shell",
        model="cube",
        color_value=color_module.azure,
        scale=Vec3(1.7, 0.42, 2.2),
        position=Vec3(0.0, 0.68, -0.28),
    )
    add_car_part(
        parent=car,
        name="car_cabin_roof",
        model="cube",
        color_value=color_module.azure,
        scale=Vec3(1.35, 0.2, 1.45),
        position=Vec3(0.0, 0.95, -0.28),
    )
    add_car_part(
        parent=car,
        name="car_windshield_front",
        model="cube",
        color_value=color_module.light_gray,
        scale=Vec3(1.26, 0.18, 0.08),
        position=Vec3(0.0, 0.83, 0.58),
        rotation=Vec3(32.0, 0.0, 0.0),
    )
    add_car_part(
        parent=car,
        name="car_windshield_rear",
        model="cube",
        color_value=color_module.light_gray,
        scale=Vec3(1.16, 0.17, 0.08),
        position=Vec3(0.0, 0.81, -1.02),
        rotation=Vec3(-30.0, 0.0, 0.0),
    )

    # Bumpers.
    add_car_part(
        parent=car,
        name="car_bumper_front",
        model="cube",
        color_value=color_module.dark_gray,
        scale=Vec3(2.22, 0.18, 0.34),
        position=Vec3(0.0, -0.03, 2.28),
    )
    add_car_part(
        parent=car,
        name="car_bumper_rear",
        model="cube",
        color_value=color_module.dark_gray,
        scale=Vec3(2.14, 0.18, 0.34),
        position=Vec3(0.0, -0.03, -2.28),
    )

    # Side skirts.
    for x_pos in (-1.04, 1.04):
        side_name = side_label(x_pos)
        add_car_part(
            parent=car,
            name=f"car_skirt_{side_name}",
            model="cube",
            color_value=color_module.dark_gray,
            scale=Vec3(0.11, 0.19, 2.85),
            position=Vec3(x_pos, -0.03, 0.02),
        )

    # Front headlights and rear lights.
    for x_pos in (-0.72, 0.72):
        side_name = side_label(x_pos)
        add_car_part(
            parent=car,
            name=f"car_headlight_{side_name}",
            model="sphere",
            color_value=color_module.yellow,
            scale=Vec3(0.24, 0.24, 0.24),
            position=Vec3(x_pos, 0.15, 2.24),
        )
        add_car_part(
            parent=car,
            name=f"car_taillight_{side_name}",
            model="sphere",
            color_value=color_module.red,
            scale=Vec3(0.22, 0.22, 0.22),
            position=Vec3(x_pos, 0.18, -2.23),
        )

    # Mirrors.
    for x_pos in (-1.05, 1.05):
        side_name = side_label(x_pos)
        add_car_part(
            parent=car,
            name=f"car_mirror_arm_{side_name}",
            model="cube",
            color_value=color_module.gray,
            scale=Vec3(0.09, 0.18, 0.09),
            position=Vec3(x_pos, 0.61, 0.46),
        )
        add_car_part(
            parent=car,
            name=f"car_mirror_cap_{side_name}",
            model="cube",
            color_value=color_module.light_gray,
            scale=Vec3(0.16, 0.07, 0.2),
            position=Vec3(x_pos * 1.02, 0.67, 0.46),
        )

    # Rear spoiler.
    for x_pos in (-0.56, 0.56):
        side_name = side_label(x_pos)
        add_car_part(
            parent=car,
            name=f"car_spoiler_post_{side_name}",
            model="cube",
            color_value=color_module.dark_gray,
            scale=Vec3(0.12, 0.32, 0.12),
            position=Vec3(x_pos, 0.62, -1.96),
        )
    add_car_part(
        parent=car,
        name="car_spoiler_wing",
        model="cube",
        color_value=color_module.dark_gray,
        scale=Vec3(1.42, 0.08, 0.28),
        position=Vec3(0.0, 0.74, -1.96),
    )

    # Wheels, hubs, and wheel bars.
    wheel_offsets = ((-1.12, 1.55), (1.12, 1.55), (-1.12, -1.55), (1.12, -1.55))
    for x_pos, z_pos in wheel_offsets:
        wheel_name = wheel_label(x_pos, z_pos)
        add_car_part(
            parent=car,
            name=f"car_wheel_tire_{wheel_name}",
            model="sphere",
            color_value=color_module.black,
            scale=Vec3(0.62, 0.62, 0.62),
            position=Vec3(x_pos, -0.22, z_pos),
        )
        add_car_part(
            parent=car,
            name=f"car_wheel_hub_{wheel_name}",
            model="sphere",
            color_value=color_module.light_gray,
            scale=Vec3(0.28, 0.28, 0.28),
            position=Vec3(x_pos, -0.22, z_pos),
        )
        add_car_part(
            parent=car,
            name=f"car_wheel_bar_{wheel_name}",
            model="cube",
            color_value=color_module.dark_gray,
            scale=Vec3(0.72, 0.12, 0.16),
            position=Vec3(x_pos, -0.22, z_pos),
        )

    return car


def normalize_loaded_car_model(model: object) -> None:
    """Scale and center imported car mesh to a consistent gameplay size."""
    get_tight_bounds = getattr(model, "getTightBounds", None)
    set_scale = getattr(model, "setScale", None)
    set_pos = getattr(model, "setPos", None)
    if not callable(get_tight_bounds):
        return
    if not callable(set_scale) or not callable(set_pos):
        return

    bounds = cast("tuple[Vec3, Vec3] | None", get_tight_bounds())
    if bounds is None:
        return

    min_point, max_point = bounds
    size_x = float(max_point.x - min_point.x)
    size_z = float(max_point.z - min_point.z)
    base_length = max(size_x, size_z)
    if base_length <= 0.0:
        return

    scale_factor = CAR_TARGET_LENGTH / base_length
    set_scale(scale_factor)
    set_pos(
        -(float(min_point.x) + size_x * 0.5) * scale_factor,
        -float(min_point.y) * scale_factor,
        -(float(min_point.z) + size_z * 0.5) * scale_factor,
    )


def load_model_from_loader(loader: object, model_path: Path) -> object | None:
    """Load a model object from a Panda3D/Ursina loader if possible."""
    load_model = getattr(loader, "loadModel", None)
    if not callable(load_model):
        return None

    try:
        return cast("object", load_model(str(model_path)))
    except OSError, RuntimeError, TypeError, ValueError:
        return None


def model_is_empty(model: object) -> bool:
    """Check whether a loaded model reports itself as empty."""
    is_empty_callable = getattr(model, "isEmpty", None)
    if not callable(is_empty_callable):
        return False
    return bool(is_empty_callable())


def apply_imported_model_cull_reverse(model: object) -> None:
    """Apply reverse culling when Panda3D CullFaceAttrib is available."""
    try:
        panda3d_core = importlib.import_module("panda3d.core")
    except ModuleNotFoundError, ImportError:
        return

    cull_face_attrib = getattr(panda3d_core, "CullFaceAttrib", None)
    make_reverse = getattr(cull_face_attrib, "makeReverse", None)
    set_attrib = getattr(model, "setAttrib", None)
    if callable(make_reverse) and callable(set_attrib):
        set_attrib(make_reverse())


def spawn_imported_player() -> Entity | None:
    """Try to spawn imported car model and return None on load failure."""
    if not CAR_MODEL_FILE.exists():
        return None

    loader = getattr(getattr(application, "base", None), "loader", None)
    if loader is None:
        return None

    model = load_model_from_loader(loader, CAR_MODEL_FILE)
    if model is None:
        return None

    if model_is_empty(model):
        return None

    # Imported OBJ has inverted winding in this asset pack.
    apply_imported_model_cull_reverse(model)

    normalize_loaded_car_model(model)

    car = Entity(
        name="player_car_imported_root",
        model=model,
        position=Vec3(0.0, 0.0, 0.0),
    )
    if CAR_BASE_TEXTURE_FILE.exists():
        car.texture = CAR_BASE_TEXTURE_PATH
    return mark_lit_shadowed(car)


def spawn_player() -> Entity:
    """Spawn the external car model when available, else use fallback."""
    imported_player = spawn_imported_player()
    if imported_player is not None:
        return imported_player
    return spawn_primitive_player()
