"""Lighting and visual world setup helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

import ursina.color as color_module
from ursina import AmbientLight, DirectionalLight, Entity, Vec2, Vec3, scene

if TYPE_CHECKING:
    from fooproj.game.config import ShadowSettings


def configure_lighting(focus_entity: Entity, settings: ShadowSettings) -> None:
    """Create one shadow-casting sun light and stable local shadow bounds."""
    sun_direction = Vec3(*settings.sun_direction).normalized()
    key_light = DirectionalLight(
        shadows=True,
        shadow_map_resolution=Vec2(
            settings.shadow_map_resolution,
            settings.shadow_map_resolution,
        ),
    )
    key_light.color = color_module.white
    key_light.look_at(sun_direction)

    ambient_light = AmbientLight()
    ambient_light.color = color_module.rgba(*settings.ambient_rgba)

    scene.set_shader_input("shadow_color", color_module.black66)
    scene.set_shader_input("shadow_blur", settings.blur)
    scene.set_shader_input("shadow_bias", settings.bias)
    scene.set_shader_input("shadow_samples", settings.samples)

    shadow_bounds = Entity(
        name="shadow_bounds_focus",
        parent=focus_entity,
        model="cube",
        position=Vec3(0.0, 0.0, 0.0),
        scale=Vec3(*settings.bounds_scale),
        color=color_module.clear,
        unlit=True,
    )
    key_light.update_bounds(shadow_bounds)

    shadow_controller = Entity(name="shadow_bounds_controller")

    def update_shadow_bounds() -> None:
        key_light.update_bounds(shadow_bounds)

    shadow_controller.update = update_shadow_bounds
