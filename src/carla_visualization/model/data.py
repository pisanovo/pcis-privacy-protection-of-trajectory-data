from dataclasses import dataclass
from typing import Dict


@dataclass
class Location:
    x: float
    y: float


@dataclass
class CarlaAgentData:
    id: str
    location: Location


@dataclass
class CarlaData:
    agents: Dict[str, CarlaAgentData]
