import time
from typing import List, Union

from path_confusion.client.model.data import VehicleUpdate
from path_confusion.server.model.data import Store, AlgorithmSettings, CarlaVehicleData


async def on_new_time_interval(alg_settings: AlgorithmSettings):
    time_received = int(time.time())
    print(f"NEW TIME INTERVAL {time_received}")
    return time_received + alg_settings.time_interval - time.time()


async def on_batch_update(batch_update: List[VehicleUpdate], store: Store, alg_settings: AlgorithmSettings):
    time_received = int(time.time())

    for v_upd in batch_update:
        vehicle_data = CarlaVehicleData(
            alias=v_upd.alias,
            time=time_received,
            speed=v_upd.speed,
            location=v_upd.location)

        existing_vehicle_updates = [e for e in store.entries if not set(v_upd.alias).isdisjoint(e.alias)]
        last_vehicle_update: Union[CarlaVehicleData, None] = existing_vehicle_updates[len(existing_vehicle_updates)-1] \
            if len(existing_vehicle_updates) > 0 else None

        if last_vehicle_update and last_vehicle_update.time + alg_settings.update_rate <= time_received:
            store.entries.append(vehicle_data)
        elif not last_vehicle_update:
            store.entries.append(vehicle_data)
