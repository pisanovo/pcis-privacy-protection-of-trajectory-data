import copy
import math
import time
from typing import List, Union

import websockets
from pyproj import Geod

from path_confusion.client.model.data import VehicleUpdate
from path_confusion.model.data import Location
from path_confusion.server.model.data import Store, AlgorithmSettings, CarlaVehicleData, AlgorithmData, \
    IntervalVehicleEntry, Interval, ReleaseEntry, ServerConnections
from path_confusion.server.model.messages import MsgServerClientReleaseUpdate


async def on_new_time_interval(alg_data: AlgorithmData, store: Store, con: ServerConnections):
    now = int(time.time())
    interval = Interval(start_at=int(now - alg_data.settings.time_interval), end_at=now)

    release_interval_store = algorithm(interval, alg_data, store)
    store.release_entries.extend(release_interval_store)

    await broadcast_store(store.release_entries, con)

    return now + alg_data.settings.time_interval - time.time()


async def on_batch_update(batch_update: List[VehicleUpdate], store: Store, alg_settings: AlgorithmSettings):
    time_received = int(time.time())

    for v_upd in batch_update:
        vehicle_data = CarlaVehicleData(
            id=v_upd.id,
            time=time_received,
            speed=v_upd.speed,
            location=v_upd.location)

        last_vehicle_update = ([e for e in reversed(store.position_entries) if e.id == v_upd.id][0:1] or [None])[0]

        if last_vehicle_update and last_vehicle_update.time + alg_settings.update_rate <= time_received:
            store.position_entries.append(vehicle_data)
        elif not last_vehicle_update:
            store.position_entries.append(vehicle_data)


async def broadcast_store(release_store: List[ReleaseEntry], con: ServerConnections):
    if con.observers:
        websockets.broadcast(con.observers, MsgServerClientReleaseUpdate(
            release_store=release_store
        ).to_json())

    if con.users:
        websockets.broadcast(con.users, MsgServerClientReleaseUpdate(
            release_store=release_store
        ).to_json())


def algorithm(interval: Interval, alg_data: AlgorithmData, in_store: Store):
    g = Geod(ellps='WGS84')

    store: Store = copy.deepcopy(in_store)
    time_interval_store = [v for v in store.latest_unique_entries() if interval.start_at <= v.time <= interval.end_at]
    release_interval_store: List[ReleaseEntry] = []

    for v_int in time_interval_store:
        v = ([v for v in alg_data.data if v.id == v_int.id][0:1] or [IntervalVehicleEntry(id=v_int.id)])[0]
        v.current_gps_sample = v_int.location
        release_interval_store.append(ReleaseEntry(interval.end_at, v))

    release_candidates = []
    release_set = []

    for vehicle in alg_data.data:
        last_update = ([v for v in reversed(store.position_entries) if v.id == vehicle.id][1:2] or [None])[0]
        start_of_trip = True if not last_update else last_update.time < interval.end_at - alg_data.settings.trip_timeout

        if start_of_trip:
            vehicle.last_confusion_time = interval.end_at
        else:
            vehicle.predicted_loc = forward_location_prediction(vehicle, interval.end_at - vehicle.last_visible.time, g)

        if interval.end_at - vehicle.last_confusion_time < alg_data.settings.confusion_timeout:
            release_set.append(vehicle)
        else:
            interval_vehicle_entries = [v for e in time_interval_store for v in alg_data.data if e.id == v.id]
            vehicle.dependencies = k_nearest(vehicle, interval_vehicle_entries, alg_data.settings.k_anonymity, g)

            u = uncertainty(vehicle.predicted_loc, vehicle.dependencies, g, alg_data.settings)

            release_entry = ([r for r in release_interval_store if r.vehicle_entry.id == vehicle.id])[0]
            release_entry.uncertainty = u

            if u > alg_data.settings.uncertainty_threshold:
                release_candidates.append(vehicle)

    release_set_ids = [rs.id for rs in release_set]
    release_candidates_ids = [rc.id for rc in release_candidates]

    prune = True
    while prune:
        prune = False
        for vehicle in release_candidates:
            if any([w.id in release_set_ids or w.id in release_candidates_ids for w in vehicle.dependencies]):
                filtered_dependencies = [dep for dep in vehicle.dependencies if dep.id in release_set_ids or dep.id in release_candidates_ids]
                if uncertainty(vehicle.predicted_loc, filtered_dependencies, g, alg_data.settings) < alg_data.settings.uncertainty_threshold:
                    release_candidates.remove(vehicle)
                    prune = True

    release_set.extend(release_candidates)

    for vehicle in release_set:
        # Publish
        release_entry = ([r for r in release_interval_store if r.vehicle_entry.id == vehicle.id])[0]
        release_entry.is_in_release_set = True

        vehicle.last_visible = vehicle.current_gps_sample
        neighbors = k_nearest(vehicle, release_set, alg_data.settings.k_anonymity, g)

        if uncertainty(vehicle.predicted_loc, neighbors, g, alg_data.settings) >= alg_data.settings.uncertainty_threshold:
            vehicle.last_confusion_time = interval.end_at

    return release_interval_store


def uncertainty(predicted_loc: Location, dependencies: List[IntervalVehicleEntry], g: Geod, alg_settings: AlgorithmSettings):
    l_pi_h = []

    for vehicle in dependencies:
        distance = g.inv(vehicle.current_gps_sample.longitude, vehicle.current_gps_sample.latitude, predicted_loc.longitude, predicted_loc.latitude)[2]
        l_pi_h.append(math.exp(-distance/alg_settings.mue))

    sum_pi_h = sum(l_pi_h)
    l_pi = [pi_h / sum_pi_h for pi_h in l_pi_h]

    u = - sum([pi * math.log2(pi) for pi in l_pi])

    return u


def k_nearest(vehicle: IntervalVehicleEntry, vehicles: List[IntervalVehicleEntry], k: int, g: Geod):
    distances = [(g.inv(vehicle.current_gps_sample.longitude, vehicle.current_gps_sample.latitude,
                        v.current_gps_sample.longitude, v.current_gps_sample.latitude)[2], v)
                 for v in vehicles if v.id != vehicle.id]

    k_nearest_vehicles = [e[1] for e in sorted(distances, key=lambda x: x[0])[:k]]

    return k_nearest_vehicles


def forward_location_prediction(vehicle: IntervalVehicleEntry, t: int, g: Geod):
    distance = (vehicle.last_visible.speed.velocity_x ** 2 + vehicle.last_visible.speed.velocity_y ** 2) ** 0.5 \
               / t
    azimuth = math.degrees(math.atan2(vehicle.last_visible.speed.velocity_x, vehicle.last_visible.speed.velocity_y))
    lon, lat, _ = g.fwd(vehicle.last_visible.location.longitude, vehicle.last_visible.location.latitude, azimuth,
                        distance)

    return Location(lon, lat)
