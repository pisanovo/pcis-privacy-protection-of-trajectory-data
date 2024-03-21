from dataclasses import dataclass
from typing import List, Union

from path_confusion.model.data import Speed, Location


@dataclass
class ClientConfig:
    update_vehicles: Union[List[str], str]


@dataclass
class VehicleUpdate:
    id: str
    speed: Speed
    location: Location
