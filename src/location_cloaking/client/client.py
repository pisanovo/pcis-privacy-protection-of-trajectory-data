import argparse
import asyncio
import json
import logging
import traceback
import websockets
from typing import Type, List
from location_cloaking.client.location_handler import LocationHandler
from location_cloaking.client.model.data import ClientInstance
from location_cloaking.client.model.messages import MsgUserLSGroupJoin, MsgUserLSPolicyChange
from location_cloaking.config import LocationServerConfig, ClientConfig
from location_cloaking.location_server.model.messages import MsgLSClientInitComplete, MsgLSUserLevelIncrease
from location_cloaking.logging import setup_logger
from location_cloaking.model.messages import MsgClientLSInit

logger = setup_logger(__name__, level=logging.DEBUG)


async def message_handler(websocket, location_handler: LocationHandler):
    """
    Handles incoming messages from the location server

    :param websocket: The client-server websocket connection
    :param location_handler: Location handler
    """
    while True:
        message = await websocket.recv()
        event = json.loads(message)

        if event["type"] == "MsgLSUserLevelIncrease":
            lvl_incr = MsgLSUserLevelIncrease.from_json(message)
            await location_handler.on_message_received(lvl_incr, websocket)
        elif event["type"] == "MsgLSUserProximityEnter":
            pass
        elif event["type"] == "MsgLSUserProximityLeave":
            # Force update
            await location_handler.run_update(websocket)


async def run_location_handler(websocket, location_handler: LocationHandler):
    """
    Continuously runs the client side algorithm in fixed intervals

    :param websocket: The client-server websocket connection
    :param location_handler: Location handler
    """
    while True:
        await location_handler.run_update(websocket)
        # TODO: Let the pull rate match server speed (currently fixed value 5fps)
        await asyncio.sleep(0.2)


async def client(instance: ClientInstance):
    """
    Set up the client instance. This involves sending a client hello message, updating the policy, joining specified
    groups

    :param instance: Provided client instance
    """
    uri = f"ws://{LocationServerConfig.LISTEN_HOST}:{LocationServerConfig.LISTEN_PORT}"

    async with websockets.connect(uri) as websocket:
        # Client hello
        await websocket.send(MsgClientLSInit(
            mode="user",
            alias=instance.alias
        ).to_json())
        # Receive plane dimensions
        message = await websocket.recv()

        init_response = MsgLSClientInitComplete.from_json(message)
        plane_dimension = init_response.plane_data

        # Update policy
        await websocket.send(MsgUserLSPolicyChange(
            user_id=init_response.user_id,
            new_max_level=instance.policy.max_level
        ).to_json())

        # Join specified groups
        for group_id in instance.group_ids:
            await websocket.send(MsgUserLSGroupJoin(
                id=group_id
            ).to_json())

        location_provider: Type = ClientConfig.SOURCE_PROVIDER
        carla_location_provider = location_provider(source_instance_data=instance.source_data)

        location_handler = LocationHandler(
            carla_location_provider,
            plane_dimension,
            instance.policy,
            init_response.user_id
        )

        # Run the incoming server message handler and location stream handler
        await asyncio.gather(
            message_handler(websocket, location_handler),
            run_location_handler(websocket, location_handler)
        )


async def main(instances: List[ClientInstance]):
    # Start all client instances
    await asyncio.gather(*[client(instance) for instance in instances])


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='Location Cloaking Client',
        epilog='For more information see the project wiki'
    )
    arg_parser.add_argument(
        '-u', '--user',
        action='append',
        nargs='*',
        help='See corresponding wiki section on how to add user(s) via command line depending on the source'
    )
    arg_parser.add_argument(
        '-f', '--file',
        action='append',
        nargs='*',
        help='JSON file path(s) containing user(s). See wiki for file '
    )
    arg_parser.add_argument(
        '-s', '--source',
        default=ClientConfig.SOURCE_PROVIDER.__name__,
        help='Source provider responsible for fetching agent location.'
    )
    args = arg_parser.parse_args()
    client_instances = []

    # Fetch client instance information as command line arguments if the user provided any
    if args.user is not None:
        cmd_instances = ClientConfig.SOURCE_PROVIDER.get_instances_from_cmd(args.user)
        client_instances.extend(cmd_instances)

    # Fetch client instance information from file if the user provided a file path
    if args.file is not None:
        with open(args.file[0][0]) as f:
            data = json.load(f)

        file_instances = ClientConfig.SOURCE_PROVIDER.get_instances_from_json(data)
        client_instances.extend(file_instances)

    if len(client_instances) == 0:
        raise ValueError("You must specify at least one client instance.")

    # Filter out any client instances with the same alias
    client_alias_without_dups = list(set([alias for c in client_instances for alias in c.alias]))

    # Only allow one client instance per alias. Basically in the context of e.g. Carla the alias is a vehicle identifier
    if len(client_instances) > len(client_alias_without_dups):
        raise ValueError("Found duplicate alias ids.")

    try:
        asyncio.run(main(client_instances))
    except:
        traceback.print_exc()
    finally:
        logger.info("Program exit! Bye.")
