"""Ursina runtime bootstrap functions."""

from typing import TYPE_CHECKING, cast

import ursina.color as color_module
from ursina import EditorCamera, Entity, Sky, window
from ursina.main import Ursina
from ursina.vec3 import Vec3

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


def run_game(settings: GameSettings | None = None) -> None:
    """Run the Ursina starter sandbox."""
    active_settings = GameSettings() if settings is None else settings
    app = cast("object", Ursina(development_mode=active_settings.development_mode))

    configure_window(active_settings)

    for blueprint in starter_scene_blueprints():
        spawn_entity(blueprint)

    Sky()
    EditorCamera(enabled=True, rotation_smoothing=0)
    # Ursina's app proxy is typed as object here, so dynamic access is needed.
    run_callable = getattr(app, "run")  # noqa: B009  # B009: getattr-with-constant
    run_callable()
