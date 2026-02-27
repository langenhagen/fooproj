"""Collision and impact response systems for dynamic props."""

import importlib
from functools import cache
from time import monotonic
from typing import TYPE_CHECKING, cast

from ursina import Entity, Vec3

from fooproj.game.systems.movement import (
    compute_player_velocity,
    resolve_ground_contact,
)
from fooproj.game.systems.rivals import apply_rival_impact
from fooproj.game.systems.timing import get_frame_dt

if TYPE_CHECKING:
    from collections.abc import Callable

    from fooproj.game.config import CollisionSettings
    from fooproj.game.systems.rivals import RivalAgent
    from fooproj.game.systems.spawn_world import DynamicProp

MIN_IMPACT_SPEED = 0.1
NORMALIZE_EPSILON = 0.0001
GROUND_FRICTION = 0.97
MIN_PROP_MASS = 0.1
RIVAL_COLLISION_RADIUS = 1.7


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


def compute_push_direction(to_target: Vec3, fallback_forward: Vec3) -> Vec3:
    """Return stable collision push direction for near-zero distances."""
    if to_target.length() > NORMALIZE_EPSILON:
        return to_target.normalized()
    return fallback_forward


def maybe_trigger_rumble(
    player_speed: float,
    last_rumble_time: float,
    cooldown_seconds: float,
) -> float:
    """Trigger impact rumble if cooldown elapsed and return updated timestamp."""
    now = monotonic()
    if now - last_rumble_time >= cooldown_seconds:
        trigger_impact_rumble(player_speed)
        return now
    return last_rumble_time


def apply_prop_collision_response(
    player: Entity,
    prop: DynamicProp,
    *,
    impact_radius: float,
    player_speed: float,
) -> bool:
    """Apply one player-to-prop collision response step."""
    to_prop = prop.entity.position - player.position
    distance = to_prop.length()
    if distance >= impact_radius or player_speed <= MIN_IMPACT_SPEED:
        return False

    push_dir = compute_push_direction(to_prop, player.forward)
    penetration = impact_radius - distance
    if penetration > 0.0:
        prop.entity.position += push_dir * (penetration * 0.4)

    effective_mass = max(prop.mass, MIN_PROP_MASS)
    prop.velocity += push_dir * (player_speed * (0.8 / effective_mass))
    prop.velocity.y = max(prop.velocity.y, 1.6)
    return True


def integrate_prop_motion(prop: DynamicProp, dt: float) -> None:
    """Integrate prop movement, gravity, bounce, and ground friction."""
    prop.velocity.y -= 9.81 * dt
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


def apply_rival_collision_response(
    player: Entity,
    rival: RivalAgent,
    *,
    impact_radius: float,
    player_speed: float,
) -> bool:
    """Apply one player-to-rival collision response step."""
    if rival.is_knocked:
        return False

    to_rival = rival.entity.position - player.position
    distance = to_rival.length()
    if distance >= impact_radius or player_speed <= MIN_IMPACT_SPEED:
        return False

    push_dir = compute_push_direction(to_rival, player.forward)
    penetration = impact_radius - distance
    if penetration > 0.0:
        rival.entity.position += push_dir * (penetration * 0.4)
    apply_rival_impact(rival, push_dir, player_speed)
    return True


def install_prop_physics_controller(
    player: Entity,
    props: list[DynamicProp],
    settings: CollisionSettings,
    *,
    rivals: list[RivalAgent] | None = None,
) -> Entity:
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
            impact_radius = settings.impact_radius + prop.radius
            if apply_prop_collision_response(
                player,
                prop,
                impact_radius=impact_radius,
                player_speed=player_speed,
            ):
                last_rumble_time = maybe_trigger_rumble(
                    player_speed,
                    last_rumble_time,
                    settings.rumble_cooldown_seconds,
                )
            integrate_prop_motion(prop, dt)

        for rival in rivals or []:
            impact_radius = settings.impact_radius + RIVAL_COLLISION_RADIUS
            if apply_rival_collision_response(
                player,
                rival,
                impact_radius=impact_radius,
                player_speed=player_speed,
            ):
                last_rumble_time = maybe_trigger_rumble(
                    player_speed,
                    last_rumble_time,
                    settings.rumble_cooldown_seconds,
                )

    controller.update = controller_update
    return controller
