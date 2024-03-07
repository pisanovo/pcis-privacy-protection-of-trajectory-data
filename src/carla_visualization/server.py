import asyncio
import logging
import carla
import websockets
from typing import List
import pyproj
from carla import Map
from carla_visualization.model.data import CarlaData, Location, CarlaAgentData
from carla_visualization.model.messages import MsgVsVcAgentLocationUpd, MsgVsVcAgents, MsgVcVsClientConfigUpd, \
    MsgVsVcClientConfigSync, MsgClientVsPositionRequest, MsgVsClientPositionResponse
from location_cloaking.config import LocationServerConfig, CarlaConfig
from location_cloaking.config import VisualizationServerConfig
from location_cloaking.logging import setup_logger

logger = setup_logger(__name__, level=logging.DEBUG)

g_client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
g_client.set_timeout(CarlaConfig.TIMEOUT)
g_carla_world = g_client.get_world()
g_carla_map: Map = g_carla_world.get_map()

g_carla_data = CarlaData(agents={})
g_carla_position_websockets = []
g_carla_agents_websockets = []
g_carla_agents_stream_websockets = []


async def update_client_config(data: str):
    with open("/home/vincenzo/PycharmProjects/DataIntensiveComputing/src/location_cloaking/data/client_config.json", "w") as f:
        f.write(data)


async def read_client_config(websocket):
    with open("/home/vincenzo/PycharmProjects/DataIntensiveComputing/src/location_cloaking/data/client_config.json") as f:
        existing_data = f.read().rstrip()

    await websocket.send(MsgVsVcClientConfigSync(data=existing_data).to_json())

    while True:
        with open("/home/vincenzo/PycharmProjects/DataIntensiveComputing/src/location_cloaking/data/client_config.json") as f:
            data = f.read().rstrip()
            if data != existing_data:
                existing_data = data
                await websocket.send(MsgVsVcClientConfigSync(data=existing_data).to_json())

        await asyncio.sleep(1.0)


async def agents_stream():
    while True:
        vehicle_actors = g_carla_world.get_actors().filter("vehicle.*")
        agents: List[CarlaAgentData] = []

        for actor in vehicle_actors:
            carla_location: carla.Location = actor.get_location()
            shifted_loc = carla.Location(x=carla_location.x - 1, y=carla_location.y, z=carla_location.z)

            geo_location = g_carla_map.transform_to_geolocation(carla_location)
            geo_position_mod = g_carla_map.transform_to_geolocation(shifted_loc)

            g = pyproj.Geod(ellps='WGS84')
            _, _, dist = g.inv(geo_location.longitude, geo_location.latitude, geo_position_mod.longitude,
                               geo_position_mod.latitude)

            agent = CarlaAgentData(
                id=f"CARLA-{actor.id}",
                location=Location(x=geo_location.latitude, y=geo_location.longitude),
                great_circle_distance_factor=dist
            )
            agents.append(agent)

        websockets.broadcast(g_carla_agents_stream_websockets, MsgVsVcAgentLocationUpd(data=agents).to_json())

        await asyncio.sleep(1 / 6)

async def carla_agents_stream_handler(websocket):
    try:
        g_carla_agents_stream_websockets.append(websocket)
        await websocket.wait_closed()
    finally:
        g_carla_agents_stream_websockets.remove(websocket)


async def carla_position_handler(websocket):
    message = await websocket.recv()
    msg = MsgClientVsPositionRequest.from_json(message)
    actor: carla.Actor = g_carla_world.get_actors().find(msg.agent_id)
    actor_position: carla.Location = actor.get_location()

    await websocket.send(MsgVsClientPositionResponse(
        x=actor_position.x,
        y=actor_position.y
    ).to_json())


async def handler(websocket, path):
    if path == "/carla/agents-stream":
        await carla_agents_stream_handler(websocket)
    elif path == "/carla/position":
        await carla_position_handler(websocket)
    elif path == "/carla/update-client-config":
        message = await websocket.recv()
        update = MsgVcVsClientConfigUpd.from_json(message)
        await update_client_config(update.data)
    elif path == "/carla/client-config-stream":
        await read_client_config(websocket)


async def serve():
    print(VisualizationServerConfig.LISTEN_HOST)
    async with websockets.serve(handler, VisualizationServerConfig.LISTEN_HOST,
                                8200, ping_interval=None):
        await asyncio.Future()


async def main():
    await asyncio.gather(
        serve(),
        agents_stream()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logger.info("Program exit! Bye.")
