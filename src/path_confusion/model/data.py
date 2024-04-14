from dataclasses import dataclass


@dataclass
class Location:
    longitude: float
    latitude: float


@dataclass
class Speed:
    velocity_x: float
    velocity_y: float
