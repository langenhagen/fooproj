"""Collision and impact response systems for dynamic props."""

from __future__ import annotations

import importlib
from functools import cache
from time import monotonic
from typing import TYPE_CHECKING, cast

from ursina import Entity, Vec3

from .movement import compute_player_velocity, resolve_ground_contact
from .timing import get_frame_dt

if TYPE_CHECKING:
    from collections.abc import Callable

    from fooproj.game.systems.spawn import DynamicProp

CAR_IMPACT_RADIUS = 1.75
MIN_IMPACT_SPEED = 0.1
NORMALIZE_EPSILON = 0.0001
GROUND_FRICTION = 0.97
RUMBLE_COOLDOWN_SECONDS = 0.12
MIN_PROP_MASS = 0.1


@cache
def get_gamepad_vibrate() -> Callable[..., None] | None:
    """Resolve and cache Ursina gamepad rumble callable if available."""
    try:
        gamepad_module = importlib.import_module("ursina.gamepad")
    except ModuleNotFoundError, ImportError:
        return None

    vibrate = getattr(gamepad_module, "vibrate", None)
    if not callable(vibrate):
        return None

    return cast("Callable[..., None]", vibrate)


def trigger_impact_rumble(player_speed: float) -> None:
    """Trigger brief gamepad rumble on impact, if a controller exists."""
    if player_speed <= MIN_IMPACT_SPEED:
        return

    vibrate = get_gamepad_vibrate()
    if vibrate is None:
        return

    rumble_strength = max(0.2, min(0.9, player_speed / 18.0))
    try:
        vibrate(
            low_freq_motor=rumble_strength,
            high_freq_motor=min(1.0, (rumble_strength * 0.8) + 0.1),
            duration=0.08,
        )
    except RuntimeError, TypeError, ValueError:
        return


def install_prop_physics_controller(player: Entity, props: list[DynamicProp]) -> Entity:
    """Attach simple prop physics and player impact responses."""
    controller = Entity(name="prop_physics_controller")
    previous_player_position = Vec3(player.position)
    last_rumble_time = 0.0

    def controller_update() -> None:
        nonlocal previous_player_position, last_rumble_time

        dt = get_frame_dt()
        if dt <= 0.0:
            return

        player_velocity = compute_player_velocity(
            player.position,
            previous_player_position,
            dt,
        )
        previous_player_position = Vec3(player.position)
        player_speed = player_velocity.length()

        for prop in props:
            prop.velocity.y -= 9.81 * dt

            to_prop = prop.entity.position - player.position
            distance = to_prop.length()
            impact_radius = CAR_IMPACT_RADIUS + prop.radius
            if distance < impact_radius and player_speed > MIN_IMPACT_SPEED:
                push_dir = (
                    to_prop.normalized()
                    if distance > NORMALIZE_EPSILON
                    else player.forward
                )
                penetration = impact_radius - distance
                if penetration > 0.0:
                    prop.entity.position += push_dir * (penetration * 0.4)
                effective_mass = max(prop.mass, MIN_PROP_MASS)
                prop.velocity += push_dir * (player_speed * (0.8 / effective_mass))
                prop.velocity.y = max(prop.velocity.y, 1.6)

                now = monotonic()
                if now - last_rumble_time >= RUMBLE_COOLDOWN_SECONDS:
                    trigger_impact_rumble(player_speed)
                    last_rumble_time = now

            prop.entity.position += prop.velocity * dt

            next_y, next_velocity_y = resolve_ground_contact(
                prop.entity.y,
                prop.velocity.y,
                prop.radius,
            )
            prop.entity.y = next_y
            prop.velocity.y = next_velocity_y
            if next_y <= prop.radius + 0.001:
                prop.velocity.x *= GROUND_FRICTION
                prop.velocity.z *= GROUND_FRICTION

    controller.update = controller_update
    return controller
