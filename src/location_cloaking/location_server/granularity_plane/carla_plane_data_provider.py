import carla
from carla import Location

from location_cloaking.location_server.granularity_plane.plane_data import PlaneDataProvider
from location_cloaking.model.data import GranularityPlaneDimensions


class CarlaPlaneDataProvider(PlaneDataProvider):
    def get_plane_dimensions(self) -> GranularityPlaneDimensions:
        """
        Fetches plane dimensions for Carla

        :return: Plane dimensions
        """
        from location_cloaking.config import CarlaConfig

        client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
        client.set_timeout(CarlaConfig.TIMEOUT)

        world = client.get_world()
        carla_map = world.get_map()

        # Generate waypoints with 2 meters distance each
        waypoints = carla_map.generate_waypoints(2)

        # Apply a margin (no idea why, but this is what the "official" carla visualization does)
        margin = 50

        # Calculate plane boundaries within Carla by iterating over waypoints
        # Carla internally does not use geo coordinates
        max_x = max(waypoints, key=lambda x: x.transform.location.x).transform.location.x + margin
        max_y = max(waypoints, key=lambda x: x.transform.location.y).transform.location.y + margin
        min_x = min(waypoints, key=lambda x: x.transform.location.x).transform.location.x - margin
        min_y = min(waypoints, key=lambda x: x.transform.location.y).transform.location.y - margin

        width = max_x - min_x
        height = max_y - min_y

        # Also calculate plane boundaries on a world map, needed for visualization
        geo_min = carla_map.transform_to_geolocation(Location(x=min_x, y=max_y))
        geo_max = carla_map.transform_to_geolocation(Location(x=max_x, y=min_y))
        lon_min = geo_min.longitude
        lat_min = geo_min.latitude
        lon_max = geo_max.longitude
        lat_max = geo_max.latitude

        return GranularityPlaneDimensions(width, height, min_x, max_x, min_y, max_y, lon_min, lon_max, lat_min, lat_max)
