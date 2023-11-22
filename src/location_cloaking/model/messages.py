# from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Union

from dataclass_wizard import JSONWizard

from location_cloaking.client.model.data import VicinityShape, VicinityCircleShape, VicinityPolyShape
from location_cloaking.model.data import EncryptedUserLocation, EncryptedUserVicinity, UserLocation, UserVicinity


#
# Generic
#
@dataclass
class Message(JSONWizard):
    # Does not work unless python >= 3.10 is used with dataclass(kw_only=True) but carla is <= 3.8
    # type: str
    pass


@dataclass
class MessageError(Message):
    msg: str


@dataclass
class MsgIncrementalUpdate(Message):
    user_id: int
    level: int
    new_location: EncryptedUserLocation
    vicinity_delete: EncryptedUserVicinity
    vicinity_insert: EncryptedUserVicinity
    vicinity_shape: dict
    type = "IncrementalUpdate"


#
# Client (User/Observer) to Location User
#
@dataclass
class MsgClientLSInit(Message):
    mode: str
    alias: List[str]
    type: str = "Init"
