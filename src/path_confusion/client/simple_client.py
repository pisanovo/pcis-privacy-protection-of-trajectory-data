import asyncio
import traceback
import websockets
from typing import List
from carla_visualization.model.messages import MsgVsVcAgentLocationUpd
from path_confusion.client.model.data import ClientConfig, VehicleUpdate
from path_confusion.client.model.message import MsgClientServerBatchedVehicleUpdate
from path_confusion.config import ServerConfig
from path_confusion.model.data import Location
from path_confusion.server.model.messages import MsgServerClientConfigUpdate


async def handle_client_config_change(config: ClientConfig, websocket):
    while True:
        message = await websocket.recv()
        response = MsgServerClientConfigUpdate.from_json(message)

        config.update_vehicles = response.new_config.update_vehicles


async def periodic_vehicle_update(config: ClientConfig, websocket):
    carla_uri = f"ws://127.0.0.1:8200/carla/agents-stream"

    async with websockets.connect(carla_uri) as carla_websocket:
        while True:
            message = await carla_websocket.recv()
            response = MsgVsVcAgentLocationUpd.from_json(message)

            updates: List[VehicleUpdate] = [VehicleUpdate(
                id=v.id,
                speed=v.speed,
                location=Location(longitude=v.location.x, latitude=v.location.y)
            ) for v in response.data if config.update_vehicles == "all" or v.id in config.update_vehicles]

            await websocket.send(MsgClientServerBatchedVehicleUpdate(
                updates=updates
            ).to_json())


async def main():
    server_uri = f"ws://{ServerConfig.LISTEN_HOST}:{ServerConfig.LISTEN_PORT}/use"

    async with websockets.connect(server_uri) as websocket:
        message = await websocket.recv()
        response = MsgServerClientConfigUpdate.from_json(message)

        config = ClientConfig(response.new_config.update_vehicles)

        # Start all client instances
        await asyncio.gather(
            handle_client_config_change(config, websocket),
            periodic_vehicle_update(config, websocket)
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        traceback.print_exc()
    finally:
        print("Program exit! Bye.")
