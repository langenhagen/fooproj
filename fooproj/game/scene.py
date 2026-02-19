"""Scene blueprints for the Ursina starter world."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Vec3:
    """Simple 3D vector data container."""

    x: float
    y: float
    z: float


@dataclass(frozen=True, slots=True)
class EntityBlueprint:
    """Data-only description for spawning an Ursina entity."""

    model: str
    color_name: str
    scale: Vec3
    position: Vec3


def starter_scene_blueprints() -> tuple[EntityBlueprint, ...]:
    """Return entities for the default sandbox scene."""
    return (
        EntityBlueprint(
            model="plane",
            color_name="light_gray",
            scale=Vec3(8.0, 1.0, 8.0),
            position=Vec3(0.0, 0.0, 0.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="orange",
            scale=Vec3(1.0, 1.0, 1.0),
            position=Vec3(0.0, 0.5, 0.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="azure",
            scale=Vec3(0.4, 0.4, 0.4),
            position=Vec3(1.5, 0.2, 1.0),
        ),
    )
