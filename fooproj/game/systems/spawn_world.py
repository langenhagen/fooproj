"""World-entity spawning and dynamic-prop metadata helpers."""

from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, cast

import ursina.color as color_module
import ursina.shaders as ursina_shaders
from ursina import Entity, Vec3

from fooproj.game.scene import EntityBlueprint, starter_scene_blueprints

if TYPE_CHECKING:
    from ursina.color import Color


LIT_SHADER = cast("object", ursina_shaders.lit_with_shadows_shader)


@dataclass(slots=True)
class DynamicProp:
    """Simple dynamic prop state for lightweight physics interactions."""

    entity: Entity
    velocity: Vec3
    radius: float
    mass: float


@cache
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
