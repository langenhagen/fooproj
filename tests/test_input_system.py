"""Tests for input mapping helpers."""

from unittest import TestCase

from fooproj.game.systems.input import (
    apply_deadzone,
    compute_gamepad_axes,
    compute_keyboard_axes,
    dominant_axis,
)

CHECKER = TestCase()


def test_compute_keyboard_axes_default_zero() -> None:
    """Return zero movement when no relevant keys are held."""
    axes = compute_keyboard_axes({})
    CHECKER.assertEqual(axes, (0.0, 0.0, 0.0))


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
    CHECKER.assertEqual(axes, (0.75, 0.5, 0.75))


def test_compute_gamepad_axes_maps_ps_style_controls() -> None:
    """Map triggers and sticks to throttle/steer/look axes."""
    held = {
        "gamepad right trigger": 0.9,
        "gamepad left trigger": 0.25,
        "gamepad right shoulder": 1.0,
        "gamepad left shoulder": 0.0,
        "gamepad left stick x": -0.5,
        "gamepad right stick x": 0.4,
        "gamepad right stick y": -0.2,
    }
    forward, strafe, turn, look_x, look_y = compute_gamepad_axes(held)
    CHECKER.assertAlmostEqual(forward, 0.65, places=5)
    CHECKER.assertEqual(strafe, 1.0)
    CHECKER.assertEqual(turn, -0.5)
    CHECKER.assertAlmostEqual(look_x, 0.0048, places=5)
    CHECKER.assertAlmostEqual(look_y, -0.0024, places=5)


def test_apply_deadzone_filters_small_values() -> None:
    """Zero out tiny analog drift while keeping intentional input."""
    CHECKER.assertEqual(apply_deadzone(0.03), 0.0)
    CHECKER.assertEqual(apply_deadzone(-0.03), 0.0)
    CHECKER.assertEqual(apply_deadzone(0.2), 0.2)


def test_dominant_axis_prefers_stronger_source() -> None:
    """Choose whichever input source has larger magnitude."""
    CHECKER.assertEqual(dominant_axis(0.2, -0.6), -0.6)
    CHECKER.assertEqual(dominant_axis(-0.8, 0.4), -0.8)
