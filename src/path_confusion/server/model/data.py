from dataclasses import dataclass, field
from typing import List, Union

from path_confusion.config import AlgorithmConfig
from path_confusion.model.data import Location, Speed


@dataclass
class CarlaVehicleData:
    # epoch millis
    alias: List[str]
    time: int
    speed: Speed
    location: Location


@dataclass
class ReleaseEntry:
    # List[str] list of carla agent ids for this interval
    neighbours: List[str]
    current_gps_sample: Union[Location, None]
    omission_reason: str


@dataclass
class IntervalVehicleEntry:
    alias: List[str]
    last_confusion_time: int
    predicted_loc: Location
    last_visible: CarlaVehicleData
    # List[str] list of carla agent ids for this interval
    dependencies: List[str]
    release_data: ReleaseEntry


@dataclass
class AlgorithmSettings:
    update_rate: float = AlgorithmConfig.DEFAULT_VEHICLE_UPDATE_RATE
    time_interval: float = AlgorithmConfig.DEFAULT_TIME_INTERVAL
    uncertainty_threshold: float = AlgorithmConfig.DEFAULT_UNCERTAINTY_THRESHOLD
    confusion_timeout: float = AlgorithmConfig.DEFAULT_TIME_TO_CONFUSION
    t_guard: float = AlgorithmConfig.DEFAULT_REACQUISITION_TIME_WINDOW
    trip_timeout: float = AlgorithmConfig.DEFAULT_TRIP_TIMEOUT
    mue: float = AlgorithmConfig.DEFAULT_MUE
    k_anonymity: int = AlgorithmConfig.DEFAULT_K_ANONYMITY
    apply_sensitive_location_cloaking_extension: bool = AlgorithmConfig.DEFAULT_APPLY_LOCATION_CLOAKING_EXTENSION
    apply_windowing_extension: bool = AlgorithmConfig.DEFAULT_APPLY_WINDOWING_EXTENSION


@dataclass
class AlgorithmData:
    intervals: List[IntervalVehicleEntry] = field(default_factory=list)
    settings: AlgorithmSettings = AlgorithmSettings()
    is_live: bool = True


@dataclass
class Store:
    entries: List[CarlaVehicleData] = field(default_factory=list)


@dataclass
class ServerConnections:
    users: List[any] = field(default_factory=list)
    observers: List[any] = field(default_factory=list)
