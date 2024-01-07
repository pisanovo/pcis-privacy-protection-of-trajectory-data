# from __future__ import annotations
from dataclasses import dataclass, field

from typing import List, Dict

from location_cloaking.model.data import EncryptedGranularityLevel, Group, GranularityPlaneDimensions


@dataclass
class LSUser:
    id: int
    alias: List[str]
    websocket: any
    granularities: List[EncryptedGranularityLevel]
    vicinity_shape: dict
    proximate_users: List["LSUser"]
    groups: List["LSGroup"]
    max_level: int


@dataclass
class LSGroup(Group):
    users: List[LSUser]


@dataclass
class LocationServerInstance:
    users: List[LSUser] = field(default_factory=list)
    groups: Dict[int, LSGroup] = field(default_factory=dict)
    observers: list = field(default_factory=list)
    plane_data: GranularityPlaneDimensions = None
