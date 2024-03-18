#
# Server to Client
#
from dataclasses import dataclass
from typing import List

from location_cloaking.model.messages import Message
from path_confusion.client.model.data import ClientConfig


@dataclass
class MsgServerClientConfigUpdate(Message):
    new_config: ClientConfig
    type: str = "MsgServerClientConfigUpdate"
