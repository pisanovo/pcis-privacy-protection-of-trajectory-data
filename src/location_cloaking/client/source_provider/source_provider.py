from abc import abstractmethod
from typing import Protocol, List

from location_cloaking.client.model.data import Position, ClientInstance


class SourceProvider(Protocol):
    @abstractmethod
    def get_latest_position(self) -> Position: raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_instances_from_cmd(cmd_input: List[str]) -> List[ClientInstance]: raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_instances_from_json(json_input: dict) -> List[ClientInstance]: raise NotImplementedError
