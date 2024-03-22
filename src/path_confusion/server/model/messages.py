#
# Server to Client
#
from dataclasses import dataclass
from typing import List

from location_cloaking.model.messages import Message
from path_confusion.client.model.data import ClientConfig
from path_confusion.server.model.data import ReleaseEntry


@dataclass
class MsgServerClientConfigUpdate(Message):
    new_config: ClientConfig
    type: str = "MsgServerClientConfigUpdate"


@dataclass
class MsgServerClientReleaseUpdate(Message):
    release_store: List[ReleaseEntry]
    type: str = "MsgServerClientReleaseUpdate"
