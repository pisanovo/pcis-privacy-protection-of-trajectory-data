from abc import abstractmethod
from typing import Protocol

from location_cloaking.model.data import GranularityPlaneDimensions


class PlaneDataProvider(Protocol):
    @abstractmethod
    def get_plane_dimensions(self) -> GranularityPlaneDimensions: raise NotImplementedError
