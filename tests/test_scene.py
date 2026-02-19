"""Tests for game scene blueprint data."""

from unittest import TestCase

from fooproj.game.scene import starter_scene_blueprints


def test_starter_scene_models() -> None:
    """Define a plane and two cubes in the starter scene."""
    blueprints = starter_scene_blueprints()
    models = [blueprint.model for blueprint in blueprints]
    checker = TestCase()
    checker.assertEqual(models, ["plane", "cube", "cube"])


def test_starter_scene_positions_are_above_ground() -> None:
    """Keep all starter entities at or above y=0."""
    blueprints = starter_scene_blueprints()
    is_above_ground = all(blueprint.position.y >= 0.0 for blueprint in blueprints)
    checker = TestCase()
    checker.assertTrue(is_above_ground)
