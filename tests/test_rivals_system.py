"""Tests for AI rival traffic planning helpers."""

from math import pi
from types import SimpleNamespace
from unittest import TestCase

from ursina import Vec3

from fooproj.game.config import RivalSettings
from fooproj.game.scene import COURSE_RADIUS
from fooproj.game.systems.rivals import (
    RivalAgent,
    apply_rival_impact,
    build_rival_plans,
    compute_angle_delta,
    compute_track_position,
    interpolate_rival_speed,
    update_rival_agent,
)

CHECKER = TestCase()


def test_compute_track_position_cardinal_angles() -> None:
    """Place rivals on expected axes around the circular course."""
    north = compute_track_position(0.0, 12.0)
    east = compute_track_position(90.0, 12.0)
    south = compute_track_position(180.0, 12.0)

    CHECKER.assertAlmostEqual(north.x, 0.0, places=5)
    CHECKER.assertAlmostEqual(north.z, 12.0, places=5)
    CHECKER.assertAlmostEqual(east.x, 12.0, places=5)
    CHECKER.assertAlmostEqual(east.z, 0.0, places=5)
    CHECKER.assertAlmostEqual(south.x, 0.0, places=5)
    CHECKER.assertAlmostEqual(south.z, -12.0, places=5)


def test_compute_angle_delta_matches_linear_distance() -> None:
    """Convert linear movement around a circle into heading delta."""
    radius = 10.0
    speed = 2.0 * pi * radius
    delta = compute_angle_delta(speed=speed, radius=radius, dt=0.25)
    CHECKER.assertAlmostEqual(delta, 90.0, places=5)


def test_interpolate_rival_speed_spans_full_range() -> None:
    """Spread rival speeds deterministically from min to max."""
    first = interpolate_rival_speed(0, 5, 8.0, 16.0)
    middle = interpolate_rival_speed(2, 5, 8.0, 16.0)
    last = interpolate_rival_speed(4, 5, 8.0, 16.0)

    CHECKER.assertEqual(first, 8.0)
    CHECKER.assertEqual(last, 16.0)
    CHECKER.assertGreater(middle, first)
    CHECKER.assertLess(middle, last)


def test_build_rival_plans_generates_expected_count_and_lanes() -> None:
    """Build one plan per rival with alternating lane radii."""
    settings = RivalSettings(
        count=4,
        min_speed=6.0,
        max_speed=10.0,
        lane_offsets=(-2.0, 2.0),
    )
    plans = build_rival_plans(settings)

    CHECKER.assertEqual(len(plans), 4)
    CHECKER.assertEqual(plans[0].lane_radius, COURSE_RADIUS - 2.0)
    CHECKER.assertEqual(plans[1].lane_radius, COURSE_RADIUS + 2.0)
    CHECKER.assertEqual(plans[2].lane_radius, COURSE_RADIUS - 2.0)
    CHECKER.assertEqual(plans[3].lane_radius, COURSE_RADIUS + 2.0)
    CHECKER.assertEqual(plans[0].speed, 6.0)
    CHECKER.assertEqual(plans[-1].speed, 10.0)


def test_build_rival_plans_respects_disabled_setting() -> None:
    """Skip traffic creation when rivals are disabled."""
    plans = build_rival_plans(RivalSettings(enabled=False, count=5))
    CHECKER.assertEqual(plans, ())


def test_rival_knockback_recovers_and_rejoins_lane() -> None:
    """Knocked rivals should land and then resume lane driving."""
    entity = SimpleNamespace(position=Vec3(0.0, 0.5, COURSE_RADIUS), rotation_y=90.0)
    rival = RivalAgent(
        entity=entity,
        angle_degrees=0.0,
        orbit_radius=COURSE_RADIUS,
        lane_radius=COURSE_RADIUS,
        speed=12.0,
        bob_phase=0.0,
        velocity=Vec3(0.0, 0.0, 0.0),
    )
    apply_rival_impact(rival, Vec3(1.0, 0.0, 0.0), impact_speed=8.0)
    CHECKER.assertTrue(rival.is_knocked)

    settings = RivalSettings(bob_amplitude=0.0)
    for _ in range(200):
        update_rival_agent(rival, dt=0.016, elapsed=1.0, settings=settings)
        if not rival.is_knocked:
            break

    CHECKER.assertFalse(rival.is_knocked)
    CHECKER.assertAlmostEqual(rival.entity.position.y, 0.5, places=5)
    CHECKER.assertNotEqual(rival.orbit_radius, rival.lane_radius)
    CHECKER.assertGreaterEqual(rival.angle_degrees, 0.0)
    CHECKER.assertLessEqual(rival.angle_degrees, 360.0)
