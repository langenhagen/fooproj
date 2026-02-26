"""Tests for game scene blueprint data."""

from unittest import TestCase

from fooproj.game.scene import starter_scene_blueprints

CHECKER = TestCase()


def test_starter_scene_models() -> None:
    """Define a large mixed-shape world with a ground plane."""
    blueprints = starter_scene_blueprints()
    models = [blueprint.model for blueprint in blueprints]
    unique_models = set(models)
    CHECKER.assertEqual(models[0], "plane")
    CHECKER.assertIn("cube", unique_models)
    CHECKER.assertIn("sphere", unique_models)
    CHECKER.assertNotIn("cylinder", unique_models)
    CHECKER.assertGreaterEqual(len(models), 80)


def test_starter_scene_positions_are_above_ground() -> None:
    """Keep all starter entities at or above y=0."""
    blueprints = starter_scene_blueprints()
    is_above_ground = all(blueprint.position.y >= 0.0 for blueprint in blueprints)
    CHECKER.assertTrue(is_above_ground)


def test_starter_scene_spans_large_distances() -> None:
    """Place landmarks far from origin to show expanded world scale."""
    blueprints = starter_scene_blueprints()
    max_axis_distance = max(
        max(abs(blueprint.position.x), abs(blueprint.position.z))
        for blueprint in blueprints
    )
    CHECKER.assertGreaterEqual(max_axis_distance, 110.0)


def test_starter_scene_has_unique_exact_positions() -> None:
    """Avoid exact coordinate duplicates that imply accidental overlap."""
    blueprints = starter_scene_blueprints()
    positions = [
        (blueprint.position.x, blueprint.position.y, blueprint.position.z)
        for blueprint in blueprints
    ]
    CHECKER.assertEqual(len(positions), len(set(positions)))


def test_starter_scene_scales_stay_in_sane_bounds() -> None:
    """Keep scene primitive scales positive and below extreme outliers."""
    blueprints = starter_scene_blueprints()
    for blueprint in blueprints:
        CHECKER.assertGreater(blueprint.scale.x, 0.0)
        CHECKER.assertGreater(blueprint.scale.y, 0.0)
        CHECKER.assertGreater(blueprint.scale.z, 0.0)
        CHECKER.assertLessEqual(blueprint.scale.x, 400.0)
        CHECKER.assertLessEqual(blueprint.scale.y, 400.0)
        CHECKER.assertLessEqual(blueprint.scale.z, 400.0)


def test_starter_scene_dynamic_static_ratio_is_reasonable() -> None:
    """Maintain a mostly-static world with meaningful dynamic obstacles."""
    blueprints = starter_scene_blueprints()
    dynamic_count = sum(1 for blueprint in blueprints if blueprint.is_dynamic)
    total_count = len(blueprints)
    static_count = total_count - dynamic_count

    CHECKER.assertGreater(dynamic_count, 0)
    CHECKER.assertGreater(static_count, 0)

    dynamic_ratio = dynamic_count / total_count
    CHECKER.assertGreaterEqual(dynamic_ratio, 0.03)
    CHECKER.assertLessEqual(dynamic_ratio, 0.4)
