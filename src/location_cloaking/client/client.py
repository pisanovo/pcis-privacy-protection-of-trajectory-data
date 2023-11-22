import argparse
import asyncio
import json
import traceback
import websockets
from typing import Type, List
from location_cloaking.client.location_handler import LocationHandler
from location_cloaking.client.model.data import ClientInstance
from location_cloaking.client.model.messages import MsgUserLSGroupJoin, MsgUserLSPolicyChange
from location_cloaking.config import LocationServerConfig, ClientConfig
from location_cloaking.location_server.model.messages import MsgLSClientInitComplete, MsgLSUserLevelIncrease
from location_cloaking.model.messages import MsgClientLSInit


async def message_handler(websocket, location_handler: LocationHandler):
    while True:
        message = await websocket.recv()
        event = json.loads(message)

        if event["type"] == "MsgLSUserLevelIncrease":
            lvl_incr = MsgLSUserLevelIncrease.from_json(message)
            await location_handler.on_message_received(lvl_incr, websocket)
        elif event["type"] == "MsgLSUserProximityEnter":
            pass
        elif event["type"] == "MsgLSUserProximityLeave":
            # force update
            await location_handler.run_update(websocket)


async def run_location_handler(websocket, location_handler: LocationHandler):
    while True:
        await location_handler.run_update(websocket)
        # TODO: Let the pull rate match server speed (currently fixed value 5fps)
        await asyncio.sleep(0.2)


async def client(instance: ClientInstance):
    uri = f"ws://{LocationServerConfig.LISTEN_HOST}:{LocationServerConfig.LISTEN_PORT}"

    async with websockets.connect(uri) as websocket:
        await websocket.send(MsgClientLSInit(
            mode="user",
            alias=instance.alias
        ).to_json())
        message = await websocket.recv()

        init_response = MsgLSClientInitComplete.from_json(message)
        plane_dimension = init_response.plane_data

        await websocket.send(MsgUserLSPolicyChange(
            user_id=init_response.user_id,
            new_max_level=instance.policy.max_level
        ).to_json())

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

        await asyncio.gather(
            message_handler(websocket, location_handler),
            run_location_handler(websocket, location_handler)
        )


async def main(instances: List[ClientInstance]):
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

    if args.user is not None:
        cmd_instances = ClientConfig.SOURCE_PROVIDER.get_instances_from_cmd(args.user)
        client_instances.extend(cmd_instances)

    if args.file is not None:
        with open(args.file[0][0]) as f:
            data = json.load(f)

        file_instances = ClientConfig.SOURCE_PROVIDER.get_instances_from_json(data)
        client_instances.extend(file_instances)

    if len(client_instances) == 0:
        raise ValueError("You must specify at least one client instance.")

    client_alias_without_dups = list(set([alias for c in client_instances for alias in c.alias]))

    if len(client_instances) > len(client_alias_without_dups):
        raise ValueError("Found duplicate alias ids.")

    try:
        asyncio.run(main(client_instances))
    except:
        print(traceback.print_exc())
