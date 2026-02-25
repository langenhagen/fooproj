"""Tests for camera math helpers."""

from unittest import TestCase

from ursina import Vec3

from fooproj.game.systems.camera import compute_look_angles, compute_zoom_distance

CHECKER = TestCase()


def test_compute_look_angles_updates_yaw_and_pitch() -> None:
    """Apply look velocity to both yaw and pitch."""
    yaw, pitch = compute_look_angles(10.0, 15.0, Vec3(0.2, -0.1, 0.0), 100.0)
    CHECKER.assertAlmostEqual(yaw, 30.0, places=5)
    CHECKER.assertAlmostEqual(pitch, 5.0, places=5)


def test_compute_look_angles_clamps_pitch() -> None:
    """Clamp pitch to the configured up/down look limits."""
    _, high_pitch = compute_look_angles(0.0, 89.0, Vec3(0.0, 1.0, 0.0), 10.0)
    _, low_pitch = compute_look_angles(0.0, -89.0, Vec3(0.0, -1.0, 0.0), 10.0)
    CHECKER.assertEqual(high_pitch, 90.0)
    CHECKER.assertEqual(low_pitch, -90.0)


def test_compute_zoom_distance_scroll_up_zooms_in() -> None:
    """Decrease camera distance when scrolling up."""
    distance = compute_zoom_distance(10.0, 1, 4.0, 18.0, 1.5)
    CHECKER.assertEqual(distance, 8.5)


def test_compute_zoom_distance_scroll_down_zooms_out() -> None:
    """Increase camera distance when scrolling down."""
    distance = compute_zoom_distance(10.0, -1, 4.0, 18.0, 2.0)
    CHECKER.assertEqual(distance, 12.0)


def test_compute_zoom_distance_clamps_to_min_and_max() -> None:
    """Keep camera distance inside configured min/max bounds."""
    min_clamped = compute_zoom_distance(4.2, 1, 4.0, 18.0, 1.0)
    max_clamped = compute_zoom_distance(17.8, -1, 4.0, 18.0, 1.0)
    CHECKER.assertEqual(min_clamped, 4.0)
    CHECKER.assertEqual(max_clamped, 18.0)


def test_compute_zoom_distance_without_max_limit() -> None:
    """Allow unbounded zoom-out when max distance is disabled."""
    distance = compute_zoom_distance(18.0, -1, 4.0, None, 6.0)
    CHECKER.assertEqual(distance, 24.0)
