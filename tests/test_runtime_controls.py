"""Tests for game runtime control math helpers."""

from unittest import TestCase

from ursina import Vec3

from fooproj.game.runtime import (
    compute_keyboard_axes,
    compute_look_angles,
    compute_zoom_distance,
)


def test_compute_keyboard_axes_default_zero() -> None:
    """Return zero movement when no relevant keys are held."""
    axes = compute_keyboard_axes({})
    checker = TestCase()
    checker.assertEqual(axes, (0.0, 0.0, 0.0))


def test_compute_keyboard_axes_combines_opposites() -> None:
    """Subtract opposite directions for forward/strafe/turn axes."""
    held = {
        "up arrow": 1.0,
        "down arrow": 0.25,
        "right arrow": 1.0,
        "left arrow": 0.5,
        "page down": 0.75,
        "page up": 0.0,
    }
    axes = compute_keyboard_axes(held)
    checker = TestCase()
    checker.assertEqual(axes, (0.75, 0.5, 0.75))


def test_compute_look_angles_updates_yaw_and_pitch() -> None:
    """Apply mouse velocity to both yaw and pitch."""
    yaw, pitch = compute_look_angles(10.0, 15.0, Vec3(0.2, -0.1, 0.0), 100.0)
    checker = TestCase()
    checker.assertAlmostEqual(yaw, 30.0, places=5)
    checker.assertAlmostEqual(pitch, 5.0, places=5)


def test_compute_look_angles_clamps_pitch() -> None:
    """Clamp pitch to the configured up/down look limits."""
    _, high_pitch = compute_look_angles(0.0, 69.0, Vec3(0.0, 1.0, 0.0), 10.0)
    _, low_pitch = compute_look_angles(0.0, -69.0, Vec3(0.0, -1.0, 0.0), 10.0)
    checker = TestCase()
    checker.assertEqual(high_pitch, 70.0)
    checker.assertEqual(low_pitch, -70.0)


def test_compute_zoom_distance_scroll_up_zooms_in() -> None:
    """Decrease camera distance when scrolling up."""
    distance = compute_zoom_distance(10.0, 1, 4.0, 18.0, 1.5)
    checker = TestCase()
    checker.assertEqual(distance, 8.5)


def test_compute_zoom_distance_scroll_down_zooms_out() -> None:
    """Increase camera distance when scrolling down."""
    distance = compute_zoom_distance(10.0, -1, 4.0, 18.0, 2.0)
    checker = TestCase()
    checker.assertEqual(distance, 12.0)


def test_compute_zoom_distance_clamps_to_min_and_max() -> None:
    """Keep camera distance inside configured min/max bounds."""
    min_clamped = compute_zoom_distance(4.2, 1, 4.0, 18.0, 1.0)
    max_clamped = compute_zoom_distance(17.8, -1, 4.0, 18.0, 1.0)
    checker = TestCase()
    checker.assertEqual(min_clamped, 4.0)
    checker.assertEqual(max_clamped, 18.0)
