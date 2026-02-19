"""Tests for game scene blueprint data."""

from fooproj.game.scene import starter_scene_blueprints


def test_starter_scene_models() -> None:
    """Define a plane and two cubes in the starter scene."""
    blueprints = starter_scene_blueprints()
    assert [blueprint.model for blueprint in blueprints] == ["plane", "cube", "cube"]


def test_starter_scene_positions_are_above_ground() -> None:
    """Keep all starter entities at or above y=0."""
    blueprints = starter_scene_blueprints()
    assert all(blueprint.position.y >= 0.0 for blueprint in blueprints)
