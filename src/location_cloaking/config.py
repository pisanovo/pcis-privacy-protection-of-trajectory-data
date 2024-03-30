from typing import Type
from location_cloaking.client.source_provider.carla_workaround_sprovider import CarlaWorkaroundSourceProvider
from location_cloaking.client.source_provider.source_provider import SourceProvider
from location_cloaking.location_server.granularity_plane.carla_plane_data_provider import CarlaPlaneDataProvider
from location_cloaking.location_server.granularity_plane.plane_data import PlaneDataProvider
import os


class Config:
    ENVIRONMENT = "dev"


class ClientConfig:
    # The source provider used to fetch vehicle positions
    SOURCE_PROVIDER: Type[SourceProvider] = CarlaWorkaroundSourceProvider


# Location Server config
class LocationServerConfig:
    # The provider used to fetch the dimensions of the algorithm area
    PLANE_DATA_PROVIDER: Type[PlaneDataProvider] = CarlaPlaneDataProvider
    LISTEN_HOST = "127.0.0.1"
    LISTEN_PORT = 8456
    LISTEN_PROXY_PORT = 8200


class VisualizationServerConfig:
    LISTEN_HOST = "127.0.0.1"


# Carla config (not used at the moment since multiple connections to one Carla instance can be buggy...)
class CarlaConfig:
    HOST = os.getenv('CARLA_URL') or "127.0.0.1"
    PORT = int(os.getenv('CARLA_PORT') or 2000)
    TIMEOUT = 25.0
