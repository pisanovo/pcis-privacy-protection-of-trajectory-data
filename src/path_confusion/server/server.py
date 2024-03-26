import asyncio
import json
import logging
import time
import traceback
from os import listdir
from os.path import join, isfile

import websockets

from location_cloaking.logging import setup_logger
from path_confusion.client.model.data import ClientConfig
from path_confusion.client.model.message import MsgClientServerBatchedVehicleUpdate
from path_confusion.config import Config, ServerConfig, AlgorithmConfig
from path_confusion.server.event_handler import on_batch_update, on_new_time_interval, broadcast_settings, \
    on_save_recording, on_load_recording, on_settings_change, on_relevant_vehicles_change, on_go_live, \
    on_delete_recording, on_reset
from path_confusion.server.model.data import ServerConnections, AlgorithmData, Store
from path_confusion.server.model.messages import MsgServerClientConfigUpdate, MsgServerObserverSettingsUpdate, \
    MsgServerObserverAvailableRecordings, MsgServerClientReleaseUpdate, MsgObserverServerAddRecording, \
    MsgObserverServerLoadRecording, MsgObserverServerChangeSettings, MsgServerObserverVehicles, \
    MsgObserverServerChangeRelevantVehicles, MsgServerActionComplete, MsgObserverServerGoLive, \
    MsgObserverServerDeleteRecording, MsgObserverServerReset

logger = setup_logger(__name__, level=logging.DEBUG)

connections = ServerConnections()
algorithm_data = AlgorithmData()
store = Store()


async def wait_on_time_interval():
    while True:
        if algorithm_data.is_live:
            next_interval_timeout = await on_new_time_interval(alg_data=algorithm_data, store=store, con=connections)
            await asyncio.sleep(next_interval_timeout)
        else:
            await asyncio.sleep(algorithm_data.settings.update_rate)


async def use(websocket):
    """

    """
    try:
        connections.users.append(websocket)

        await websocket.send(MsgServerClientConfigUpdate(
            new_config=ClientConfig(update_vehicles="all")
        ).to_json())

        async for message in websocket:
            event = json.loads(message)

            if event["type"] == MsgClientServerBatchedVehicleUpdate.__name__:
                upd = MsgClientServerBatchedVehicleUpdate.from_json(message).updates

                if algorithm_data.is_live:
                    await on_batch_update(batch_update=upd, store=store, alg_data=algorithm_data)
            else:
                raise ValueError
    finally:
        connections.users.remove(websocket)


async def observe(websocket):
    """

    """
    try:
        connections.observers.append(websocket)

        await websocket.send(MsgServerObserverSettingsUpdate(
            settings=algorithm_data.settings,
            is_live=algorithm_data.is_live
        ).to_json())

        path = ServerConfig.RECORDINGS_STORAGE_PATH
        recording_file_names = [f for f in listdir(path) if isfile(join(path, f))]

        await websocket.send(MsgServerObserverAvailableRecordings(
            file_names=recording_file_names
        ).to_json())

        await websocket.send(MsgServerClientReleaseUpdate(
            release_store=store.release_entries
        ).to_json())

        await websocket.send(MsgServerObserverVehicles(
            available_vehicles=list(set([e.id for e in store.position_entries])),
            relevant_vehicles=algorithm_data.relevant_vehicles
        ).to_json())

        # Keep the connection open, but don't receive any messages
        await websocket.wait_closed()

    finally:
        connections.observers.remove(websocket)


async def command(websocket):
    async for message in websocket:
        event = json.loads(message)
        print(event)

        if event["type"] == MsgObserverServerAddRecording.__name__:
            msg = MsgObserverServerAddRecording.from_json(message)
            await on_save_recording(msg.name, algorithm_data, store, connections)
        elif event["type"] == MsgObserverServerLoadRecording.__name__:
            msg = MsgObserverServerLoadRecording.from_json(message)
            await on_load_recording(msg.recording_file_name, algorithm_data, store, connections)
        elif event["type"] == MsgObserverServerDeleteRecording.__name__:
            msg = MsgObserverServerDeleteRecording.from_json(message)
            await on_delete_recording(msg.recording_file_name, connections)
        elif event["type"] == MsgObserverServerChangeSettings.__name__:
            msg = MsgObserverServerChangeSettings.from_json(message)
            await on_settings_change(msg.new_settings, algorithm_data, store, connections)
        elif event["type"] == MsgObserverServerChangeRelevantVehicles.__name__:
            msg = MsgObserverServerChangeRelevantVehicles.from_json(message)
            await on_relevant_vehicles_change(msg.ids, algorithm_data, store, connections)
        elif event["type"] == MsgObserverServerGoLive.__name__:
            await on_go_live(algorithm_data, store, connections)
        elif event["type"] == MsgObserverServerReset.__name__:
            await on_reset(algorithm_data, store, connections)

        await websocket.send(MsgServerActionComplete().to_json())
        break


async def handler(websocket, path):
    """

    """
    if path == "/observe" and Config.ENVIRONMENT == "dev":
        await observe(websocket)
    elif path == "/command":
        await command(websocket)
    elif path == "/use":
        await use(websocket)
    else:
        raise ValueError


async def serve():
    async with websockets.serve(handler, ServerConfig.LISTEN_HOST, ServerConfig.LISTEN_PORT, ping_interval=None):
        await asyncio.Future()


async def main():
    await asyncio.gather(
        serve(),
        wait_on_time_interval()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        traceback.print_exc()
    finally:
        logger.info("Program exit! Bye.")
