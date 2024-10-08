#
# Server to Client
#
from dataclasses import dataclass
from typing import List

from location_cloaking.model.messages import Message
from path_confusion.client.model.data import ClientConfig
from path_confusion.server.model.data import ReleaseEntry, AlgorithmSettings


@dataclass
class MsgServerActionComplete(Message):
    type: str = "MsgServerActionComplete"


@dataclass
class MsgServerClientConfigUpdate(Message):
    new_config: ClientConfig
    type: str = "MsgServerClientConfigUpdate"


@dataclass
class MsgServerClientReleaseUpdate(Message):
    release_store: List[ReleaseEntry]
    type: str = "MsgServerClientReleaseUpdate"


@dataclass
class MsgServerObserverSettingsUpdate(Message):
    settings: AlgorithmSettings
    is_live: bool
    type: str = "MsgServerObserverSettingsUpdate"


@dataclass
class MsgServerObserverAvailableRecordings(Message):
    file_names: List[str]
    type: str = "MsgServerObserverAvailableRecordings"


@dataclass
class MsgObserverServerAddRecording(Message):
    name: str
    type: str = "MsgObserverServerAddRecording"


@dataclass
class MsgObserverServerGoLive(Message):
    name: str
    type: str = "MsgObserverServerGoLive"


@dataclass
class MsgObserverServerReset(Message):
    type: str = "MsgObserverServerReset"


@dataclass
class MsgObserverServerLoadRecording(Message):
    recording_file_name: str
    type: str = "MsgObserverServerLoadRecording"


@dataclass
class MsgObserverServerDeleteRecording(Message):
    recording_file_name: str
    type: str = "MsgObserverServerDeleteRecording"


@dataclass
class MsgObserverServerChangeSettings(Message):
    new_settings: AlgorithmSettings
    type: str = "MsgObserverServerChangeSettings"


@dataclass
class MsgServerObserverVehicles(Message):
    available_vehicles: List[str]
    relevant_vehicles: List[str]
    type: str = "MsgServerObserverVehicles"


@dataclass
class MsgObserverServerChangeRelevantVehicles(Message):
    ids: List[str]
    type: str = "MsgObserverServerChangeRelevantVehicles"
