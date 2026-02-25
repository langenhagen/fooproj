"""Tests for movement and kinematic helpers."""

from unittest import TestCase

from ursina import Vec3

from fooproj.game.systems.movement import (
    compute_player_velocity,
    compute_smoothed_forward_speed,
    resolve_ground_contact,
)

CHECKER = TestCase()


def test_compute_smoothed_forward_speed_accelerates_to_target() -> None:
    """Move speed toward requested target instead of snapping instantly."""
    next_speed = compute_smoothed_forward_speed(0.0, 1.0, 60.0, 0.1)
    CHECKER.assertGreater(next_speed, 0.0)
    CHECKER.assertLess(next_speed, 60.0)


def test_compute_smoothed_forward_speed_respects_analog_input() -> None:
    """Use fractional trigger input for proportional target speed."""
    next_speed = compute_smoothed_forward_speed(0.0, 0.5, 60.0, 0.1)
    CHECKER.assertGreater(next_speed, 0.0)
    CHECKER.assertLess(next_speed, 30.0)


def test_compute_smoothed_forward_speed_brakes_when_reversing() -> None:
    """Reverse input should reduce current forward speed rapidly."""
    next_speed = compute_smoothed_forward_speed(30.0, -1.0, 60.0, 0.1)
    CHECKER.assertLess(next_speed, 30.0)


def test_compute_player_velocity_uses_delta_time() -> None:
    """Calculate player frame velocity from position delta and dt."""
    velocity = compute_player_velocity(
        Vec3(2.0, 0.0, -4.0),
        Vec3(1.0, 0.0, -2.0),
        0.5,
    )
    CHECKER.assertEqual(velocity, Vec3(2.0, 0.0, -4.0))


def test_compute_player_velocity_handles_zero_dt() -> None:
    """Return zero velocity when dt is zero or negative."""
    velocity = compute_player_velocity(
        Vec3(10.0, 0.0, 5.0),
        Vec3(1.0, 0.0, -2.0),
        0.0,
    )
    CHECKER.assertEqual(velocity, Vec3(0.0, 0.0, 0.0))


def test_resolve_ground_contact_bounces_and_clamps() -> None:
    """Clamp below-ground props and reverse downward velocity."""
    y_pos, y_vel = resolve_ground_contact(position_y=0.1, velocity_y=-3.0, radius=0.45)
    CHECKER.assertEqual(y_pos, 0.45)
    CHECKER.assertAlmostEqual(y_vel, 1.05, places=5)


def test_resolve_ground_contact_keeps_above_ground_state() -> None:
    """Leave position and velocity unchanged when already above ground."""
    y_pos, y_vel = resolve_ground_contact(position_y=0.8, velocity_y=0.2, radius=0.45)
    CHECKER.assertEqual(y_pos, 0.8)
    CHECKER.assertEqual(y_vel, 0.2)
