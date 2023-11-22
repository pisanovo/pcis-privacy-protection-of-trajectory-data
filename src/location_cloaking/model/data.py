from __future__ import annotations
from dataclasses import dataclass


#
# Generic
#
@dataclass
class Position:
    x: float
    y: float


@dataclass
class Group:
    id: int


@dataclass
class GranularityPlaneDimensions:
    width: float
    height: float
    x_min: float
    x_max: float
    y_min: float
    y_max: float


#
# User
#
USER_LOC_UNDEFINED = -1


@dataclass
class UserLocation:
    granule: int


@dataclass
class UserVicinity:
    granules: list[int]


@dataclass
class GranularityLevel:
    location: UserLocation
    vicinity: UserVicinity


#
# Encrypted Variations
#
@dataclass
class EncryptedUserLocation(UserLocation):
    pass


@dataclass
class EncryptedUserVicinity(UserVicinity):
    pass


@dataclass
class EncryptedGranularityLevel:
    encrypted_location: EncryptedUserLocation
    encrypted_vicinity: EncryptedUserVicinity
