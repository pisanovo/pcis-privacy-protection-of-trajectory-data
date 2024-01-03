from typing import Type
from location_cloaking.client.source_provider.carla_source_provider import CarlaSourceProvider
from location_cloaking.client.source_provider.carla_workaround_sprovider import CarlaWorkaroundSourceProvider
from location_cloaking.client.source_provider.source_provider import SourceProvider
from location_cloaking.location_server.granularity_plane.carla_plane_data_provider import CarlaPlaneDataProvider
from location_cloaking.location_server.granularity_plane.plane_data import PlaneDataProvider


class Config:
    ENVIRONMENT = "dev"


class ClientConfig:
    SOURCE_PROVIDER: Type[SourceProvider] = CarlaWorkaroundSourceProvider


class LocationServerConfig:
    PLANE_DATA_PROVIDER: Type[PlaneDataProvider] = CarlaPlaneDataProvider
    LISTEN_HOST = "127.0.0.1"
    LISTEN_PORT = 8456


class CarlaConfig:
    HOST = "127.0.0.1"
    PORT = 2000
    TIMEOUT = 25.0
