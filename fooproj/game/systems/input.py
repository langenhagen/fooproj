"""Input mapping helpers for keyboard, gamepad, and look controls."""

from ursina import Vec3

GAMEPAD_DEADZONE = 0.08
GAMEPAD_LOOK_SENSITIVITY = 0.012


def compute_keyboard_axes(held: dict[str, float]) -> tuple[float, float, float]:
    """Compute movement axes from the current held-key mapping."""
    forward_amount = held.get("up arrow", 0.0) - held.get("down arrow", 0.0)
    strafe_amount = held.get("right arrow", 0.0) - held.get("left arrow", 0.0)
    turn_amount = held.get("page down", 0.0) - held.get("page up", 0.0)
    return forward_amount, strafe_amount, turn_amount


def apply_deadzone(value: float, deadzone: float = GAMEPAD_DEADZONE) -> float:
    """Clamp small analog stick/trigger noise to zero."""
    if abs(value) < deadzone:
        return 0.0
    return value


def compute_gamepad_axes(
    held: dict[str, float],
) -> tuple[float, float, float, float, float]:
    """Map gamepad triggers and sticks to movement and camera look inputs."""
    forward_amount = apply_deadzone(
        held.get("gamepad right trigger", 0.0) - held.get("gamepad left trigger", 0.0),
    )
    strafe_amount = held.get("gamepad right shoulder", 0.0) - held.get(
        "gamepad left shoulder",
        0.0,
    )
    turn_amount = apply_deadzone(held.get("gamepad left stick x", 0.0))
    look_x = apply_deadzone(held.get("gamepad right stick x", 0.0))
    look_y = apply_deadzone(held.get("gamepad right stick y", 0.0))
    return (
        forward_amount,
        strafe_amount,
        turn_amount,
        look_x * GAMEPAD_LOOK_SENSITIVITY,
        look_y * GAMEPAD_LOOK_SENSITIVITY,
    )


def dominant_axis(primary: float, secondary: float) -> float:
    """Return the stronger of two axis sources by absolute value."""
    return primary if abs(primary) >= abs(secondary) else secondary


def compute_control_axes(
    held: dict[str, float],
    mouse_velocity: Vec3,
) -> tuple[float, float, float, Vec3]:
    """Combine keyboard, gamepad, and mouse into one control vector set."""
    keyboard_forward, keyboard_strafe, keyboard_turn = compute_keyboard_axes(held)
    gamepad_forward, gamepad_strafe, gamepad_turn, gamepad_look_x, gamepad_look_y = (
        compute_gamepad_axes(held)
    )
    return (
        dominant_axis(keyboard_forward, gamepad_forward),
        dominant_axis(keyboard_strafe, gamepad_strafe),
        dominant_axis(keyboard_turn, gamepad_turn),
        Vec3(
            dominant_axis(mouse_velocity.x, gamepad_look_x),
            dominant_axis(mouse_velocity.y, gamepad_look_y),
            0.0,
        ),
    )
