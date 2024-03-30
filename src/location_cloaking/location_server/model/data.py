# from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from location_cloaking.model.data import EncryptedGranularityLevel, Group, GranularityPlaneDimensions


# A location service user/vehicle
@dataclass
class LSUser:
    # The user location service ID != Carla ID
    id: int
    # list of names the vehicle is known as, first element always contains the Carla ID (CARLA-xx)
    alias: List[str]
    websocket: any
    granularities: List[EncryptedGranularityLevel]
    vicinity_shape: dict
    proximate_users: List["LSUser"]
    # joined groups by the user
    groups: List["LSGroup"]
    # policy max level
    max_level: int


# A location service group that can be joined by users
@dataclass
class LSGroup(Group):
    users: List[LSUser]


@dataclass
class LocationServerInstance:
    users: List[LSUser] = field(default_factory=list)
    groups: Dict[int, LSGroup] = field(default_factory=dict)
    observers: list = field(default_factory=list)
    plane_data: GranularityPlaneDimensions = None


# Used to synchronize frontend since incremental updates are used otherwise
# Contains the full algorithm state for one user/vehicle
@dataclass
class UserSync:
    user_id: int
    alias: List[str]
    level: int
    granularities: List[EncryptedGranularityLevel]
    vicinity_shape: dict
