import random
import time
from typing import List

import carla
from carla import Transform, Map, World, Actor
from haversine import haversine

from location_cloaking.config import CarlaConfig
from location_cloaking.utils.map.agents.navigation.basic_agent import BasicAgent
from location_cloaking.utils.map.agents.navigation.behavior_agent import BehaviorAgent
from location_cloaking.utils.map.agents.navigation.global_route_planner import GlobalRoutePlanner


def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []


def get_closest_elevated_waypoint_transform(geo, waypoints):
    min_dist = None
    closest_waypoint_transform = None

    for waypoint in waypoints:
        transform = waypoint.transform
        location = transform.location
        geo_location = map.transform_to_geolocation(location)

        dist = haversine(geo, (geo_location.latitude, geo_location.longitude))

        if min_dist is None or dist < min_dist:
            min_dist = dist
            closest_waypoint_transform = transform

    closest_waypoint_transform.location.z = closest_waypoint_transform.location.z + 4

    return closest_waypoint_transform

try:
    num_vehicles = 5

    client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
    client.set_timeout(CarlaConfig.TIMEOUT)

    world: World = client.get_world()

    settings = world.get_settings()
    settings.synchronous_mode = True  # Enables synchronous mode
    # settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    map: Map = world.get_map()

    spawn_points: List[Transform] = map.get_spawn_points()
    blueprints = get_actor_blueprints(world, "vehicle.mercedes.coupe_2020", "2")

    grp_inst = GlobalRoutePlanner(map, 5.0)

    vehicles = []

    for i in range(0, num_vehicles):
        blueprint = random.choice(blueprints)
        start_point = random.choice(spawn_points)
        waypoint = map.get_waypoint(start_point.location)

        while grp_inst._road_id_to_edge[waypoint.road_id] is None:
            spawn_points.remove(start_point)
            start_point = random.choice(spawn_points)
            waypoint = map.get_waypoint(start_point.location)

        transform = waypoint.transform
        transform.location.z = transform.location.z + 4
        actor: Actor = world.spawn_actor(blueprint, transform)

        # DO NOT REMOVE - actor location will be unstable initially, location is available only one tick after spawn!!
        world.tick()
        world.tick()
        agent = BehaviorAgent(actor, behavior='normal', opt_dict={"ignore_traffic_lights": True}, grp_inst=grp_inst)

        # end_point = random.choice(spawn_points)
        # agent.set_destination(end_point.location)

        keep_trying = True
        while keep_trying:
            end_point = random.choice(spawn_points)
            try:
                # connect
                agent.set_destination(end_point.location)
                keep_trying = False
            except Exception as e:
                pass

        vehicles.append((actor, agent))

    while True:
        start = time.time()
        world.tick()
        end = time.time()
        print("TICK TIME", end - start)
        start2 = time.time()
        for vehicle in vehicles:
            actor, agent = vehicle

            if agent.done():
                keep_trying = True
                while keep_trying:
                    end_point = random.choice(spawn_points)
                    try:
                        # connect
                        agent.set_destination(end_point.location)
                        keep_trying = False
                    except Exception as e:
                        pass
            # start = time.time()
            actor.apply_control(agent.run_step())
        end2 = time.time()
        print("ALL CONTROL TIME", end2 - start2)

finally:
    for vehicle in vehicles:
        actor, agent = vehicle

        r = actor.destroy()
        print(r)
