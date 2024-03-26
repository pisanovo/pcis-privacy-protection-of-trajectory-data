from dataclasses import dataclass, field
from typing import List, Union

from dataclass_wizard import JSONWizard

from path_confusion.config import AlgorithmConfig
from path_confusion.model.data import Location, Speed


@dataclass
class Interval:
    # epoch millis
    start_at: int
    end_at: int


@dataclass
class CarlaVehicleData:
    # epoch millis
    id: str
    time: int
    speed: Speed
    location: Location


@dataclass
class IntervalVehicleEntry:
    id: str
    last_confusion_time: int = None
    current_gps_sample: CarlaVehicleData = None
    predicted_loc: Location = None
    last_visible: CarlaVehicleData = None
    # List[str] list of carla agent ids for this interval
    dependencies: List[str] = None
    neighbors: List[str] = None


@dataclass
class ReleaseEntry:
    created_at_time: int
    vehicle_entry: IntervalVehicleEntry
    uncertainty_interval: Union[float, None] = None
    uncertainty_release_set: Union[float, None] = None
    is_in_release_set: bool = False


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
    data: List[IntervalVehicleEntry] = field(default_factory=list)
    relevant_vehicles: List[str] = field(default_factory=list)
    settings: AlgorithmSettings = AlgorithmSettings()
    is_live: bool = True


@dataclass
class Store:
    position_entries: List[CarlaVehicleData] = field(default_factory=list)
    release_entries: List[ReleaseEntry] = field(default_factory=list)

    def interval_unique_entries(self, interval: Interval):
        visited = []
        filtered_store = []
        for v in reversed(self.position_entries):
            if v.id not in visited and interval.start_at <= v.time < interval.end_at:
                visited.append(v.id)
                filtered_store.insert(0, v)

        return filtered_store


@dataclass
class ServerConnections:
    users: List[any] = field(default_factory=list)
    observers: List[any] = field(default_factory=list)


@dataclass
class Dump(JSONWizard):
    name: str
    recorded_at_time: int
    settings: AlgorithmSettings
    position_entries: List[CarlaVehicleData]
