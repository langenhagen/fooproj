"""Movement and kinematic helper logic for runtime systems."""

from typing import cast

from ursina import Vec3, lerp_exponential_decay

BOUNCE_DAMPING = 0.35
MIN_BOUNCE_SPEED = 0.25
FORWARD_MAX_SPEED_MULTIPLIER = 3.0
FORWARD_ACCELERATION_RATE = 9.0
FORWARD_DECELERATION_RATE = 11.0
FORWARD_BRAKE_RATE = 16.0


def compute_smoothed_forward_speed(
    current_speed: float,
    forward_input: float,
    max_speed: float,
    dt: float,
) -> float:
    """Compute smooth forward speed from digital/analog acceleration input."""
    if dt <= 0.0:
        return current_speed

    target_speed = forward_input * max_speed
    if target_speed == 0.0:
        response_rate = FORWARD_DECELERATION_RATE
    elif current_speed == 0.0 or (target_speed * current_speed) > 0.0:
        if abs(target_speed) >= abs(current_speed):
            response_rate = FORWARD_ACCELERATION_RATE
        else:
            response_rate = FORWARD_DECELERATION_RATE
    else:
        response_rate = FORWARD_BRAKE_RATE

    return cast(
        "float",
        lerp_exponential_decay(current_speed, target_speed, dt * response_rate),
    )


def compute_player_velocity(
    current_position: Vec3,
    previous_position: Vec3,
    dt: float,
) -> Vec3:
    """Compute frame velocity from two positions and a delta time."""
    if dt <= 0.0:
        return Vec3(0.0, 0.0, 0.0)

    inverse_dt = 1.0 / dt
    return Vec3(
        (current_position.x - previous_position.x) * inverse_dt,
        (current_position.y - previous_position.y) * inverse_dt,
        (current_position.z - previous_position.z) * inverse_dt,
    )


def resolve_ground_contact(
    position_y: float,
    velocity_y: float,
    radius: float,
) -> tuple[float, float]:
    """Clamp a prop above ground and bounce vertical velocity."""
    if position_y >= radius:
        return position_y, velocity_y

    next_y = radius
    next_velocity_y = velocity_y
    if velocity_y < 0.0:
        next_velocity_y = -velocity_y * BOUNCE_DAMPING
        if abs(next_velocity_y) < MIN_BOUNCE_SPEED:
            next_velocity_y = 0.0

    return next_y, next_velocity_y
