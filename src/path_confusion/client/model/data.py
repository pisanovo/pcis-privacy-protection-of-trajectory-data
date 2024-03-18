from dataclasses import dataclass
from typing import List, Union

from path_confusion.model.data import Speed, Location


@dataclass
class ClientConfig:
    update_vehicles: Union[List[List[str]], str]


@dataclass
class VehicleUpdate:
    alias: List[str]
    speed: Speed
    location: Location
