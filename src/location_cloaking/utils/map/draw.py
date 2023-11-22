import time

import carla

from location_cloaking.config import CarlaConfig

client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)

world = client.get_world()
map = world.get_map()

waypoints = map.generate_waypoints(1)
for w in waypoints:
    time.sleep(0.005)
    world.debug.draw_string(w.transform.location, 'O', draw_shadow=False,
                                       color=carla.Color(r=102, g=80, b=15), life_time=6000.0,
                                       persistent_lines=True)