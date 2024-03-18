import asyncio
import json
import logging
import time
import traceback

import websockets

from location_cloaking.logging import setup_logger
from path_confusion.client.model.data import ClientConfig
from path_confusion.client.model.message import MsgClientServerBatchedVehicleUpdate
from path_confusion.config import Config, ServerConfig, AlgorithmConfig
from path_confusion.server.event_handler import on_batch_update, on_new_time_interval
from path_confusion.server.model.data import ServerConnections, AlgorithmData, Store
from path_confusion.server.model.messages import MsgServerClientConfigUpdate

logger = setup_logger(__name__, level=logging.DEBUG)

connections = ServerConnections()
algorithm_data = AlgorithmData()
store = Store()


async def wait_on_time_interval():
    while True:
        next_interval_timeout = await on_new_time_interval(alg_settings=algorithm_data.settings)
        await asyncio.sleep(next_interval_timeout)


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
                await on_batch_update(batch_update=upd, store=store, alg_settings=algorithm_data.settings)
            else:
                raise ValueError
    finally:
        connections.users.remove(websocket)


async def observe(websocket):
    """

    """
    try:
        connections.observers.append(websocket)
    finally:
        connections.observers.remove(websocket)


async def handler(websocket, path):
    """

    """
    if path == "/observe" and Config.ENVIRONMENT == "dev":
        await observe(websocket)
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
