from dataclasses import dataclass
from typing import List, Union

from path_confusion.model.data import Position, Speed


@dataclass
class CarlaVehicleUpdate:
    # epoch millis
    id: int
    time: int
    speed: Speed
    position: Position


@dataclass
class ReleaseEntry:
    # List[str] list of carla agent ids for this interval
    neighbours: List[str]
    current_gps_sample: Union[Position, None]


@dataclass
class IntervalVehicleEntry:
    id: int
    last_confusion_time: int
    predicted_pos: Position
    last_visible: CarlaVehicleUpdate
    # List[str] list of carla agent ids for this interval
    dependencies: List[str]
    release_data: ReleaseEntry


@dataclass
class AlgorithmData:
    intervals: List[IntervalVehicleEntry]


@dataclass
class Store:
    entries: List[CarlaVehicleUpdate]


@dataclass
class AlgorithmSettings:
    time_interval: float
    uncertainty_threshold: float
    confusion_timeout: float
    t_guard: float
    trip_timeout: float
    mue: float
