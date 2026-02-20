"""Tests for game scene blueprint data."""

from unittest import TestCase

from fooproj.game.scene import starter_scene_blueprints


def test_starter_scene_models() -> None:
    """Define a ground plane plus multiple landmark cubes."""
    blueprints = starter_scene_blueprints()
    models = [blueprint.model for blueprint in blueprints]
    checker = TestCase()
    checker.assertEqual(models[0], "plane")
    checker.assertTrue(all(model == "cube" for model in models[1:]))
    checker.assertGreaterEqual(len(models), 9)


def test_starter_scene_positions_are_above_ground() -> None:
    """Keep all starter entities at or above y=0."""
    blueprints = starter_scene_blueprints()
    is_above_ground = all(blueprint.position.y >= 0.0 for blueprint in blueprints)
    checker = TestCase()
    checker.assertTrue(is_above_ground)
