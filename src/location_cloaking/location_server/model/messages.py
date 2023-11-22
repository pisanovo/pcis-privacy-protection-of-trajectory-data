# from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List

from location_cloaking.model.data import GranularityPlaneDimensions
from location_cloaking.model.messages import MsgIncrementalUpdate, Message, MessageError


#
# Location Server to Client
#
@dataclass
class MsgLSClientInitComplete(Message):
    user_id: int
    type = "InitComplete"
    plane_data: GranularityPlaneDimensions = None


#
# Location Server to User
#
@dataclass
class MsgLSUserProximityEnter(Message):
    other_user_id: int
    group_id: int
    type: str = "MsgLSUserProximityEnter"


@dataclass
class MsgLSUserProximityLeave(Message):
    other_user_id: int
    group_id: int
    type: str = "MsgLSUserProximityLeave"


@dataclass
class MsgLSUserLevelIncrease(Message):
    to_level: int
    type: str = "MsgLSUserLevelIncrease"


#
# Location Server to Observer
#
@dataclass
class MsgLSObserverIncUpd(MsgIncrementalUpdate):
    alias: List[str]
    type: str = "MsgLSObserverIncUpd"


@dataclass
class MsgLSObserverProximity(Message):
    proximity_enter: bool
    user_affected_id: int
    user_affected_alias: List[str]
    user_entered_id: int
    user_entered_alias: List[str]
    group_id: int
    type: str = "MsgLSObserverProximity"


#
# Fault
# Always Location Server to Client (User/Observer)
#


@dataclass
class MsgErrorProcessCommand(MessageError):
    type: str = "MsgErrorProcessCommand"
    msg: str = "Could not process command."


@dataclass
class MsgErrorInvalidGroup(MessageError):
    type: str = "ErrorInvalidGroup"
    msg: str = "Group does not exist."


@dataclass
class MsgErrorGroupAlreadyJoined(Message):
    type: str = "ErrorGroupAlreadyJoined"
    msg: str = "You already joined this group before."


@dataclass
class MsgErrorNotGroupMember(Message):
    type: str = "ErrorNotGroupMember"
    msg: str = "You are not part of this group."
