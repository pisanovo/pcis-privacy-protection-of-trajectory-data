from dataclasses import dataclass
from typing import Dict


@dataclass
class Location:
    x: float
    y: float


@dataclass
class Speed:
    velocity_x: float
    velocity_y: float


@dataclass
class CarlaAgentData:
    id: str
    location: Location
    speed: Speed
    # One Carla unit to meters on a map for vehicle
    great_circle_distance_factor: float


@dataclass
class CarlaData:
    agents: Dict[str, CarlaAgentData]
