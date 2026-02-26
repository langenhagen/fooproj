"""AI rival traffic spawning and circular track update helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, copysign, cos, degrees, hypot, pi, radians, sin
from typing import TYPE_CHECKING, cast

import ursina.color as color_module
from ursina import Entity, Vec3

from fooproj.game.scene import COURSE_RADIUS
from fooproj.game.systems.spawn_world import mark_lit_shadowed
from fooproj.game.systems.timing import get_frame_dt

if TYPE_CHECKING:
    from ursina.color import Color

    from fooproj.game.config import RivalSettings


RIVAL_COLOR_SEQUENCE = ("azure", "yellow", "magenta", "orange", "lime", "cyan")
RIVAL_BODY_SCALE = Vec3(1.7, 0.62, 3.1)
RIVAL_BASE_HEIGHT = 0.5
RIVAL_KNOCK_GRAVITY = 9.81
RIVAL_KNOCK_FRICTION = 0.985
RIVAL_MIN_AIR_SPEED = 0.08


@dataclass(frozen=True, slots=True)
class RivalPlan:
    """Data-only rival spawn plan for deterministic setup."""

    index: int
    color_name: str
    angle_degrees: float
    lane_radius: float
    speed: float
    bob_phase: float


@dataclass(slots=True)
class RivalAgent:
    """Runtime state for one moving rival vehicle."""

    entity: Entity
    angle_degrees: float
    orbit_radius: float
    lane_radius: float
    speed: float
    bob_phase: float
    velocity: Vec3
    is_knocked: bool = False


def resolve_rival_color(color_name: str) -> Color:
    """Resolve a color name from Ursina's built-in color palette."""
    return cast("Color", getattr(color_module, color_name, color_module.white))


def compute_track_position(
    angle_degrees: float,
    radius: float,
    height: float = RIVAL_BASE_HEIGHT,
) -> Vec3:
    """Compute a circular track position from heading angle and radius."""
    angle_radians = radians(angle_degrees)
    return Vec3(sin(angle_radians) * radius, height, cos(angle_radians) * radius)


def compute_angle_delta(speed: float, radius: float, dt: float) -> float:
    """Convert linear speed to a circular angle delta in degrees."""
    if dt <= 0.0 or radius <= 0.0:
        return 0.0

    circumference = 2.0 * pi * radius
    return (speed / circumference) * 360.0 * dt


def interpolate_rival_speed(
    index: int,
    count: int,
    min_speed: float,
    max_speed: float,
) -> float:
    """Return deterministic rival speed spread across configured range."""
    if count <= 1:
        return min_speed

    speed_span = max_speed - min_speed
    speed_ratio = index / (count - 1)
    return min_speed + (speed_span * speed_ratio)


def build_rival_plans(
    settings: RivalSettings,
    *,
    course_radius: float = COURSE_RADIUS,
) -> tuple[RivalPlan, ...]:
    """Build deterministic rival plans from settings."""
    if not settings.enabled or settings.count <= 0:
        return ()

    lane_offsets = settings.lane_offsets or (0.0,)
    min_speed = min(settings.min_speed, settings.max_speed)
    max_speed = max(settings.min_speed, settings.max_speed)

    plans: list[RivalPlan] = []
    for rival_index in range(settings.count):
        lane_offset = lane_offsets[rival_index % len(lane_offsets)]
        lane_radius = max(4.0, course_radius + lane_offset)
        start_angle = (360.0 / settings.count) * rival_index
        speed = interpolate_rival_speed(
            rival_index,
            settings.count,
            min_speed,
            max_speed,
        )
        bob_phase = (2.0 * pi / settings.count) * rival_index
        plans.append(
            RivalPlan(
                index=rival_index,
                color_name=RIVAL_COLOR_SEQUENCE[
                    rival_index % len(RIVAL_COLOR_SEQUENCE)
                ],
                angle_degrees=start_angle,
                lane_radius=lane_radius,
                speed=speed,
                bob_phase=bob_phase,
            ),
        )
    return tuple(plans)


def spawn_rival_from_plan(plan: RivalPlan) -> RivalAgent:
    """Spawn one rival vehicle from plan data."""
    rival_root = Entity(
        name=f"rival_vehicle_{plan.index}",
        position=compute_track_position(plan.angle_degrees, plan.lane_radius),
    )

    # Explicit child names make scene hierarchy debugging easier in Ursina.
    body = Entity(
        parent=rival_root,
        name=f"rival_body_{plan.index}",
        model="cube",
        color=resolve_rival_color(plan.color_name),
        scale=RIVAL_BODY_SCALE,
        position=Vec3(0.0, 0.0, 0.0),
    )
    mark_lit_shadowed(body)

    canopy = Entity(
        parent=rival_root,
        name=f"rival_canopy_{plan.index}",
        model="cube",
        color=color_module.smoke,
        scale=Vec3(1.1, 0.28, 1.2),
        position=Vec3(0.0, 0.42, -0.18),
    )
    mark_lit_shadowed(canopy)

    for wheel_index, (x_pos, z_pos) in enumerate(
        ((-0.78, 1.05), (0.78, 1.05), (-0.78, -1.05), (0.78, -1.05)),
    ):
        wheel = Entity(
            parent=rival_root,
            name=f"rival_wheel_{plan.index}_{wheel_index}",
            model="sphere",
            color=color_module.black,
            scale=Vec3(0.34, 0.34, 0.34),
            position=Vec3(x_pos, -0.18, z_pos),
        )
        mark_lit_shadowed(wheel)

    rival_root.rotation_y = plan.angle_degrees + 90.0
    return RivalAgent(
        entity=rival_root,
        angle_degrees=plan.angle_degrees,
        orbit_radius=plan.lane_radius,
        lane_radius=plan.lane_radius,
        speed=plan.speed,
        bob_phase=plan.bob_phase,
        velocity=Vec3(0.0, 0.0, 0.0),
    )


def apply_rival_impact(
    agent: RivalAgent,
    push_direction: Vec3,
    impact_speed: float,
) -> None:
    """Apply knockback impulse so a rival bounces away from collisions."""
    agent.velocity += push_direction * (impact_speed * 0.9)
    agent.velocity.y = max(agent.velocity.y, 1.8)
    agent.is_knocked = True


def rejoin_track_lane(agent: RivalAgent) -> None:
    """Start lane rejoin from landed location without teleporting."""
    current = agent.entity.position
    agent.angle_degrees = degrees(atan2(current.x, current.z)) % 360.0
    agent.orbit_radius = max(4.0, hypot(current.x, current.z))
    agent.entity.position = Vec3(current.x, RIVAL_BASE_HEIGHT, current.z)
    agent.entity.rotation_y = agent.angle_degrees + 90.0
    agent.velocity = Vec3(0.0, 0.0, 0.0)
    agent.is_knocked = False


def move_radius_toward_lane(
    orbit_radius: float,
    lane_radius: float,
    rejoin_rate: float,
    dt: float,
) -> float:
    """Move current orbit radius toward target lane at fixed rate."""
    radius_delta = lane_radius - orbit_radius
    max_step = max(0.0, rejoin_rate) * dt
    if abs(radius_delta) <= max_step:
        return lane_radius
    return orbit_radius + (copysign(max_step, radius_delta))


def update_rival_agent(
    agent: RivalAgent,
    *,
    dt: float,
    elapsed: float,
    settings: RivalSettings,
) -> None:
    """Advance one rival car around the track and update its transform."""
    if agent.is_knocked:
        agent.velocity.y -= RIVAL_KNOCK_GRAVITY * dt
        agent.entity.position += agent.velocity * dt
        agent.velocity.x *= RIVAL_KNOCK_FRICTION
        agent.velocity.z *= RIVAL_KNOCK_FRICTION

        if (
            agent.entity.position.y <= RIVAL_BASE_HEIGHT
            and agent.velocity.y <= RIVAL_MIN_AIR_SPEED
        ):
            rejoin_track_lane(agent)
        return

    agent.orbit_radius = move_radius_toward_lane(
        agent.orbit_radius,
        agent.lane_radius,
        settings.lane_rejoin_rate,
        dt,
    )

    agent.angle_degrees = (
        agent.angle_degrees + compute_angle_delta(agent.speed, agent.orbit_radius, dt)
    ) % 360.0

    bob_offset = sin((elapsed * settings.bob_speed) + agent.bob_phase)
    bob_height = bob_offset * settings.bob_amplitude
    agent.entity.position = compute_track_position(
        agent.angle_degrees,
        agent.orbit_radius,
        RIVAL_BASE_HEIGHT + bob_height,
    )
    agent.entity.rotation_y = agent.angle_degrees + 90.0


def install_rival_controller(settings: RivalSettings) -> list[RivalAgent]:
    """Spawn rival cars and attach a frame-update traffic controller."""
    rival_plans = build_rival_plans(settings)
    if not rival_plans:
        return []

    rival_agents = [spawn_rival_from_plan(plan) for plan in rival_plans]
    traffic_controller = Entity(name="rival_traffic_controller")
    elapsed = 0.0

    def traffic_update() -> None:
        nonlocal elapsed

        dt = get_frame_dt()
        if dt <= 0.0:
            return

        elapsed += dt
        for rival in rival_agents:
            update_rival_agent(
                rival,
                dt=dt,
                elapsed=elapsed,
                settings=settings,
            )

    traffic_controller.update = traffic_update
    return rival_agents
