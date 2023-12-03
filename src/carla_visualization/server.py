import asyncio
import functools
import json
import logging
import carla
import websockets
from typing import List
from carla_visualization.model.data import CarlaData, Location, CarlaAgentData
from carla_visualization.model.messages import MsgVsVcAgentLocationUpd, MsgVsVcAgents
from location_cloaking.config import LocationServerConfig, CarlaConfig
from location_cloaking.logging import setup_logger

logger = setup_logger(__name__, level=logging.DEBUG)

g_client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
g_client.set_timeout(CarlaConfig.TIMEOUT)
g_carla_world = g_client.get_world()
g_carla_map = g_carla_world.get_map()

g_carla_data = CarlaData(agents={})
g_carla_position_websockets = []
g_carla_agents_websockets = []


async def carla_position_sync(actor_data: CarlaData):
    while True:
        vehicle_actors = g_carla_world.get_actors().filter("vehicle.*")
        updated_actors: List[CarlaAgentData] = []
        for actor in vehicle_actors:
            carla_location = actor.get_location()
            if actor.id in actor_data.agents:
                agent_data = actor_data.agents[actor.id]
                actor_location_data = agent_data.location
                if actor_location_data.x != carla_location.x or actor_location_data.y != carla_location.y:
                    geo_location = g_carla_map.transform_to_geolocation(carla_location)
                    agent_data.location = Location(x=geo_location.latitude, y=geo_location.longitude)
                    updated_actors.append(agent_data)
            else:
                actor_data.agents[actor.id] = CarlaAgentData(
                    id=actor.id,
                    location=Location(x=carla_location.x, y=carla_location.y)
                )
                updated_actors.append(actor_data.agents[actor.id])

        if updated_actors:
            # print(updated_actors)
            websockets.broadcast(g_carla_position_websockets, MsgVsVcAgentLocationUpd(data=updated_actors).to_json())
            
        await asyncio.sleep(1 / 60)


async def carla_agents_sync():
    while True:
        vehicle_actors = g_carla_world.get_actors().filter("vehicle.*")
        agent_ids = []

        for actor in vehicle_actors:
            agent_ids.append(actor.id)

        agent_ids.sort()

        labeled_agent_ids = []

        for actor_id in agent_ids:
            labeled_agent_ids.append(f"CARLA-id-{actor_id}")

        websockets.broadcast(g_carla_agents_websockets, MsgVsVcAgents(data=labeled_agent_ids).to_json())

        await asyncio.sleep(1)


async def carla_position_stream_handler(websocket):
    try:
        g_carla_position_websockets.append(websocket)
        await websocket.wait_closed()
    finally:
        g_carla_position_websockets.remove(websocket)


async def carla_agents_handler(websocket):
    try:
        g_carla_agents_websockets.append(websocket)
        await websocket.wait_closed()
    finally:
        g_carla_agents_websockets.remove(websocket)


async def handler(websocket, path):
    if path == "/carla/position-stream":
        await carla_position_stream_handler(websocket)
    elif path == "/carla/agents":
        await carla_agents_handler(websocket)


async def serve():
    async with websockets.serve(handler, LocationServerConfig.LISTEN_HOST,
                                8200, ping_interval=None):
        await asyncio.Future()


async def main():
    await asyncio.gather(
        serve(),
        carla_position_sync(g_carla_data),
        carla_agents_sync()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        logger.info("Program exit! Bye.")
