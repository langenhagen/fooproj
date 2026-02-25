"""Lighting and visual world setup helpers."""

import ursina.color as color_module
from ursina import AmbientLight, DirectionalLight, Entity, Vec2, Vec3, scene


def configure_lighting(focus_entity: Entity) -> None:
    """Create one shadow-casting sun light and stable local shadow bounds."""
    sun_direction = Vec3(0.8, -1.2, -0.5).normalized()
    key_light = DirectionalLight(shadows=True, shadow_map_resolution=Vec2(4096, 4096))
    key_light.color = color_module.white
    key_light.look_at(sun_direction)

    ambient_light = AmbientLight()
    ambient_light.color = color_module.rgba(0.22, 0.24, 0.28, 1.0)

    scene.set_shader_input("shadow_color", color_module.black66)
    scene.set_shader_input("shadow_blur", 0.0008)
    scene.set_shader_input("shadow_bias", 0.0005)
    scene.set_shader_input("shadow_samples", 3)

    shadow_bounds = Entity(
        name="shadow_bounds_focus",
        parent=focus_entity,
        model="cube",
        position=Vec3(0.0, 0.0, 0.0),
        scale=Vec3(38.0, 20.0, 38.0),
        color=color_module.clear,
        unlit=True,
    )
    key_light.update_bounds(shadow_bounds)

    shadow_controller = Entity(name="shadow_bounds_controller")

    def update_shadow_bounds() -> None:
        key_light.update_bounds(shadow_bounds)

    shadow_controller.update = update_shadow_bounds
