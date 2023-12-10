from dataclasses import dataclass
from typing import List

from dataclass_wizard import JSONWizard

from carla_visualization.model.data import CarlaAgentData


@dataclass
class Message(JSONWizard):
    # Does not work unless python >= 3.10 is used with dataclass(kw_only=True) but carla is <= 3.8
    # type: str
    pass


@dataclass
class MsgVsVcAgentLocationUpd(Message):
    data: List[CarlaAgentData]
    type = "LocationUpdate"


@dataclass
class MsgVsVcAgents(Message):
    data: List[str]
    type = "Agents"
