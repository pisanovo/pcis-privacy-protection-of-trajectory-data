from dataclasses import dataclass
from typing import List, Optional

from location_cloaking.client.model.data import VicinityShape
from location_cloaking.model.data import GranularityLevel


@dataclass
class VisualizeEntry:
    alias: List[str]
    color: (int, int, int)
    level: int
    granularities: List[GranularityLevel]
    vicinity_shape: dict
