# from __future__ import annotations
from dataclasses import dataclass

from location_cloaking.model.messages import MsgIncrementalUpdate, Message
# from location_cloaking.model.data import EncryptedUserLocation, EncryptedUserVicinity, UserLocation, UserVicinity


#
# User to Location Server
#
@dataclass
class MsgUserLSIncUpd(MsgIncrementalUpdate):
    type: str = "MsgUserLSIncUpd"


@dataclass
class MsgUserLSGroupJoin(Message):
    id: int
    type: str = "MsgUserLSGroupJoin"


@dataclass
class MsgUserLSGroupLeave(Message):
    id: int
    type: str = "MsgUserLSGroupLeave"


@dataclass
class MsgUserLSPolicyChange(Message):
    user_id: int
    new_max_level: int
    type: str = "MsgUserLSPolicyChange"
