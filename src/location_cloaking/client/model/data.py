from __future__ import annotations
from dataclasses import dataclass

from location_cloaking.model.data import Position


@dataclass
class ClientInstance:
    source_data: any
    alias: list[str]
    policy: Policy
    group_ids: list[int]


@dataclass
class VicinityShape:
    pass


@dataclass
class VicinityCircleShape(VicinityShape):
    radius: float


@dataclass
class VicinityPolyShape(VicinityShape):
    # Polygon points around an agent which is at position (0,0)
    poly_points: list[Position]


@dataclass
class Policy:
    max_level: int
    vicinity_shape: VicinityShape
    current_level: int = 0


@dataclass
class User:
    alias: list[str]
    user_id: int
