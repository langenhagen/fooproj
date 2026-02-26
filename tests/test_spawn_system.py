"""Tests for spawn system helpers."""

from unittest import TestCase

from ursina import Vec3

from fooproj.game.systems.spawn_world import compute_prop_mass

CHECKER = TestCase()


def test_compute_prop_mass_scales_with_size() -> None:
    """Give larger props higher mass than smaller ones."""
    small = compute_prop_mass(Vec3(0.8, 0.8, 0.8))
    large = compute_prop_mass(Vec3(1.0, 2.5, 1.0))
    CHECKER.assertGreater(large, small)
