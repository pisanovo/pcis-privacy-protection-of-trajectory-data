import asyncio
import json
import logging
import traceback
import websockets
from event_handler import on_message_received, on_policy_change_received
from location_cloaking.client.model.messages import MsgUserLSIncUpd, MsgUserLSGroupJoin, MsgUserLSGroupLeave, \
    MsgUserLSPolicyChange
from location_cloaking.config import LocationServerConfig, Config
from location_cloaking.logging import setup_logger
from location_cloaking.model.messages import MsgClientLSInit
from model.data import *
from model.messages import *
from granularity_plane.manual_plane_data_provider import ManualPlaneDataProvider

logger = setup_logger(__name__, level=logging.DEBUG)

data = LocationServerInstance()


async def error(websocket, cls, **kwargs):
    """
    Send error message from specified message class type and provided arguments

    :param websocket: User/observer websocket connection
    :param cls: Class representing message type
    :param kwargs: Arguments provided for the corresponding message type
    """
    await websocket.send(cls(**kwargs).to_json())


async def use(websocket, init_msg: MsgClientLSInit):
    """
    Server logic handling user connections

    :param websocket: User websocket connection
    :param init_msg: Message containing user hello
    """
    if init_msg.alias is None:
        init_msg.alias = []

    max_id = max([user.id for user in data.users]) if len(data.users) > 0 else 1
    user = LSUser(
        id=max_id + 1,
        alias=init_msg.alias,
        websocket=websocket,
        granularities=[],
        proximate_users=[],
        groups=[],
        max_level=0
    )

    try:
        # Create new user entry
        data.users.append(user)
        # Send confirmation together with plane data
        await websocket.send(MsgLSClientInitComplete(
            user_id=user.id,
            plane_data=data.plane_data
        ).to_json())

        async for message in websocket:
            event = json.loads(message)

            if event["type"] == "MsgUserLSIncUpd":
                upd = MsgUserLSIncUpd.from_json(message)
                await on_message_received(user, upd, data)
            elif event["type"] == "MsgUserLSGroupJoin":
                join_msg = MsgUserLSGroupJoin.from_json(message)

                # Received invalid group id
                if join_msg.id < 0:
                    raise ValueError

                if join_msg.id not in data.groups.keys():
                    data.groups[join_msg.id] = LSGroup(id=join_msg.id, users=[])

                group = data.groups[join_msg.id]

                if user in group.users:
                    # User has already joined the group
                    await error(websocket, MsgErrorGroupAlreadyJoined)
                else:
                    user.groups.append(group)
                    group.users.append(user)
            elif event["type"] == "MsgUserLSGroupLeave":
                leave_msg = MsgUserLSGroupLeave.from_json(message)
                try:
                    group = data.groups[leave_msg.id]

                    if user not in group.users:
                        # User never joined the group
                        await error(websocket, MsgErrorNotGroupMember)
                    else:
                        user.groups.remove(group)
                        group.users.remove(user)
                except KeyError:
                    await error(websocket, MsgErrorInvalidGroup)
            elif event["type"] == "MsgUserLSPolicyChange":
                new_policy_msg = MsgUserLSPolicyChange.from_json(message)
                user = [u for u in data.users if u.id == new_policy_msg.user_id][0]

                on_policy_change_received(new_policy_msg, user)
            else:
                raise ValueError
    except:
        logger.error(f"Failed to process message with user {user.id}")
        # Send a generic processing error message before terminating the connection
        await error(websocket, MsgErrorProcessCommand)
    finally:
        # Cleanup disconnecter user
        for group in user.groups:
            group.users.remove(user)
            for group_user in group.users:
                if user in group_user.proximate_users:
                    group_user.proximate_users.remove(user)

        data.users.remove(user)


async def observe(websocket):
    """
    Server logic to handle observer connections. Observer example: Carla visualization frontend

    :param websocket: Observer websocket connection
    """
    try:
        data.observers.append(websocket)
        # Send confirmation together with plane data
        await websocket.send(MsgLSClientInitComplete(plane_data=data.plane_data, user_id=-1).to_json())
        # Keep the connection open, but don't receive any messages
        await websocket.wait_closed()
    finally:
        # Cleanup disconnected observer
        data.observers.remove(websocket)


async def handler(websocket, path):
    """
    Handles incoming websocket connections by identifying if a user or observer opened the connection

    :param websocket: User or observer websocket connection
    :param path: The requested resource path
    """
    try:
        if path == "/observe" and Config.ENVIRONMENT == "dev":
            await observe(websocket)

        message = await websocket.recv()
        init_msg = MsgClientLSInit.from_json(message)

        if init_msg.mode == "user":
            await use(websocket, init_msg)
        else:
            raise ValueError
    except:
        logger.error(f"Failed to process message in handler")
        # Send a generic processing error message before terminating the connection
        await error(websocket, MsgErrorProcessCommand)


async def main():
    try:
        # Fetch plane dimensions needed by users and observers from the provider
        provider = LocationServerConfig.PLANE_DATA_PROVIDER
        plane_dimensions = provider().get_plane_dimensions()
    except:
        # Fallback to manual input
        provider = ManualPlaneDataProvider
        plane_dimensions = provider().get_plane_dimensions()

    data.plane_data = plane_dimensions

    logger.debug(f"[PlaneData/{provider.__name__}] "
                 f"Plane dimensions, width: {plane_dimensions.width}, height: {plane_dimensions.height}")

    async with websockets.serve(handler, LocationServerConfig.LISTEN_HOST, LocationServerConfig.LISTEN_PORT, ping_interval=None):
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        traceback.print_exc()
    finally:
        logger.info("Program exit! Bye.")
