from dataclasses import dataclass
from typing import List
from location_cloaking.model.messages import Message
from path_confusion.client.model.data import VehicleUpdate


#
# Client to Server
#
@dataclass
class MsgClientServerBatchedVehicleUpdate(Message):
    updates: List[VehicleUpdate]
    type: str = "MsgClientServerBatchedVehicleUpdate"
