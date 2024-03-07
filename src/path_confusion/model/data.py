from dataclasses import dataclass


@dataclass
class Position:
    longitude: float
    latitude: float


@dataclass
class Speed:
    velocity_x: float
    velocity_y: float
