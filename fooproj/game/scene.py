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
            scale=Vec3(24.0, 1.0, 24.0),
            position=Vec3(0.0, 0.0, 0.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="red",
            scale=Vec3(1.2, 1.2, 1.2),
            position=Vec3(6.0, 0.6, 6.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="azure",
            scale=Vec3(1.2, 1.2, 1.2),
            position=Vec3(-6.0, 0.6, 6.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="orange",
            scale=Vec3(1.2, 1.2, 1.2),
            position=Vec3(6.0, 0.6, -6.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="violet",
            scale=Vec3(1.2, 1.2, 1.2),
            position=Vec3(-6.0, 0.6, -6.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="lime",
            scale=Vec3(1.0, 2.5, 1.0),
            position=Vec3(0.0, 1.25, 10.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="yellow",
            scale=Vec3(1.0, 2.5, 1.0),
            position=Vec3(10.0, 1.25, 0.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="cyan",
            scale=Vec3(1.0, 2.5, 1.0),
            position=Vec3(0.0, 1.25, -10.0),
        ),
        EntityBlueprint(
            model="cube",
            color_name="magenta",
            scale=Vec3(1.0, 2.5, 1.0),
            position=Vec3(-10.0, 1.25, 0.0),
        ),
    )
