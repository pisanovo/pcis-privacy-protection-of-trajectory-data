import carla
from location_cloaking.location_server.granularity_plane.plane_data import PlaneDataProvider
from location_cloaking.model.data import GranularityPlaneDimensions


class CarlaPlaneDataProvider(PlaneDataProvider):
    def get_plane_dimensions(self) -> GranularityPlaneDimensions:
        from location_cloaking.config import CarlaConfig

        client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
        client.set_timeout(CarlaConfig.TIMEOUT)

        world = client.get_world()
        carla_map = world.get_map()
        waypoints = carla_map.generate_waypoints(2)
        margin = 50

        max_x = max(waypoints, key=lambda x: x.transform.location.xodr_str).transform.location.xodr_str + margin
        max_y = max(waypoints, key=lambda x: x.transform.location.y).transform.location.y + margin
        min_x = min(waypoints, key=lambda x: x.transform.location.xodr_str).transform.location.xodr_str - margin
        min_y = min(waypoints, key=lambda x: x.transform.location.y).transform.location.y - margin

        width = max_x - min_x
        height = max_y - min_y

        return GranularityPlaneDimensions(width, height, min_x, max_x, min_y, max_y)
