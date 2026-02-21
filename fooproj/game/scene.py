"""Scene blueprints for the Ursina driving sandbox world."""

from dataclasses import dataclass
from math import cos, radians, sin


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
    """Return entities for the expanded sandbox scene."""
    blueprints: list[EntityBlueprint] = [
        EntityBlueprint(
            model="plane",
            color_name="light_gray",
            scale=Vec3(260.0, 1.0, 260.0),
            position=Vec3(0.0, 0.0, 0.0),
        ),
    ]

    blueprints.extend(_perimeter_columns())
    blueprints.extend(_orbital_props())
    blueprints.extend(_cardinal_landmarks())
    return tuple(blueprints)


def _perimeter_columns() -> list[EntityBlueprint]:
    """Create a large boundary ring of heavy columns."""
    columns: list[EntityBlueprint] = []
    colors = ("cyan", "magenta", "yellow", "lime")
    color_index = 0
    edge = 110.0

    for step in range(-90, 91, 18):
        edge_positions = (
            (float(step), edge),
            (float(step), -edge),
            (edge, float(step)),
            (-edge, float(step)),
        )
        for x_pos, z_pos in edge_positions:
            columns.append(
                EntityBlueprint(
                    model="cube",
                    color_name=colors[color_index % len(colors)],
                    scale=Vec3(2.4, 6.2, 2.4),
                    position=Vec3(x_pos, 3.1, z_pos),
                ),
            )
            color_index += 1

    return columns


def orbital_prop_scale(model_name: str, ring_index: int) -> Vec3:
    """Return scale for orbital props based on model and ring."""
    if model_name == "sphere":
        sphere_scale = 1.1 + (ring_index * 0.18)
        return Vec3(sphere_scale, sphere_scale, sphere_scale)

    return Vec3(
        1.2 + (ring_index * 0.16),
        1.4 + (ring_index * 0.28),
        1.2 + (ring_index * 0.16),
    )


def _orbital_props() -> list[EntityBlueprint]:
    """Create large concentric rings of mixed-shape dynamic props."""
    props: list[EntityBlueprint] = []
    models = ("cube", "sphere")
    colors = ("red", "azure", "orange", "violet", "lime", "yellow", "cyan", "magenta")
    radii = (18.0, 34.0, 52.0, 72.0, 94.0)
    points_per_ring = 14

    for ring_index, radius in enumerate(radii):
        for point_index in range(points_per_ring):
            angle = ((360.0 / points_per_ring) * point_index) + (ring_index * 8.0)
            x_pos = sin(radians(angle)) * radius
            z_pos = cos(radians(angle)) * radius

            model_name = models[(ring_index + point_index) % len(models)]
            color_name = colors[(ring_index * 3 + point_index) % len(colors)]
            scale = orbital_prop_scale(model_name, ring_index)

            props.append(
                EntityBlueprint(
                    model=model_name,
                    color_name=color_name,
                    scale=scale,
                    position=Vec3(x_pos, scale.y * 0.5, z_pos),
                ),
            )

    return props


def _cardinal_landmarks() -> list[EntityBlueprint]:
    """Create distant large landmarks to emphasize world scale."""
    landmarks: list[EntityBlueprint] = []
    layout = (
        ("cube", "orange", Vec3(9.0, 16.0, 9.0), Vec3(0.0, 8.0, 118.0)),
        ("cube", "azure", Vec3(9.0, 16.0, 9.0), Vec3(0.0, 8.0, -118.0)),
        ("cube", "yellow", Vec3(9.0, 16.0, 9.0), Vec3(118.0, 8.0, 0.0)),
        ("cube", "violet", Vec3(9.0, 16.0, 9.0), Vec3(-118.0, 8.0, 0.0)),
        ("sphere", "lime", Vec3(7.0, 7.0, 7.0), Vec3(82.0, 3.5, 82.0)),
        ("sphere", "magenta", Vec3(7.0, 7.0, 7.0), Vec3(-82.0, 3.5, 82.0)),
        ("sphere", "cyan", Vec3(7.0, 7.0, 7.0), Vec3(82.0, 3.5, -82.0)),
        ("sphere", "red", Vec3(7.0, 7.0, 7.0), Vec3(-82.0, 3.5, -82.0)),
    )

    for model_name, color_name, scale, position in layout:
        landmarks.append(
            EntityBlueprint(
                model=model_name,
                color_name=color_name,
                scale=scale,
                position=position,
            ),
        )

    return landmarks
