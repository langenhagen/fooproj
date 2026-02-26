"""Compatibility exports for world and player spawn systems."""

from .spawn_player import spawn_player
from .spawn_world import DynamicProp, compute_prop_mass, spawn_world_entities

__all__ = [
    "DynamicProp",
    "compute_prop_mass",
    "spawn_player",
    "spawn_world_entities",
]
