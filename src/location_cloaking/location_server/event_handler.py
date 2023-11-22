import websockets
from typing import Type
from location_cloaking.client.model.messages import MsgUserLSPolicyChange, MsgUserLSIncUpd
from location_cloaking.location_server.model.data import LocationServerInstance, LSUser, LSGroup
from location_cloaking.model.data import EncryptedGranularityLevel
from model.messages import *


def on_policy_change_received(new_policy_msg: MsgUserLSPolicyChange, user: LSUser):
    if new_policy_msg.new_max_level < 0:
        raise ValueError

    if new_policy_msg.new_max_level < user.max_level:
        del user.granularities[:new_policy_msg.new_max_level]

    user.max_level = new_policy_msg.new_max_level


async def message_proximity_change(
        is_vicinity_entry: bool,
        user_affected: LSUser,
        user_entered: LSUser,
        group: LSGroup,
        data: LocationServerInstance,
):
    vicinity_unicast_type: Type = MsgLSUserProximityEnter if is_vicinity_entry else MsgLSUserProximityLeave

    await user_affected.websocket.send(vicinity_unicast_type(
        other_user_id=user_entered.id,
        group_id=group.id
    ).to_json())
    if data.observers:
        websockets.broadcast(data.observers, MsgLSObserverProximity(
            proximity_enter=is_vicinity_entry,
            user_affected_id=user_affected.id,
            user_affected_alias=user_affected.alias,
            user_entered_id=user_entered.id,
            user_entered_alias=user_entered.alias,
            group_id=group.id
        ).to_json())


async def on_message_received(user: LSUser, upd: MsgUserLSIncUpd, data: LocationServerInstance):
    if data.observers:
        # Broadcast incremental update to observers
        websockets.broadcast(data.observers, MsgLSObserverIncUpd(
            user_id=user.id,
            alias=user.alias,
            level=upd.level,
            new_location=upd.new_location,
            vicinity_delete=upd.vicinity_delete,
            vicinity_insert=upd.vicinity_insert,
            vicinity_shape=upd.vicinity_shape
        ).to_json())

    if upd.level > user.max_level or upd.level < 0:
        raise ValueError

    # Truncate granularities list if level received is lower
    del user.granularities[upd.level + 1:]

    # After receiving a level increase message
    if upd.level == len(user.granularities):
        user.granularities.append(EncryptedGranularityLevel(
            encrypted_location=upd.new_location,
            encrypted_vicinity=upd.vicinity_insert
        ))
    # If we're patching an existing granularity level
    else:
        print(upd.level, len(user.granularities))
        level_location = user.granularities[upd.level].encrypted_location
        level_vicinity = user.granularities[upd.level].encrypted_vicinity
        level_vicinity.granules = [g for g in level_vicinity.granules if g not in upd.vicinity_delete.granules]
        level_vicinity.granules.extend(upd.vicinity_insert.granules)
        level_location.granule = upd.new_location.granule

    for group in user.groups:
        for group_user in group.users:
            if group_user == user or len(group_user.granularities) == 0:
                continue

            min_level = min(len(user.granularities) - 1, len(group_user.granularities) - 1,
                            user.max_level, group_user.max_level)

            user_min_level_location = user.granularities[min_level].encrypted_location
            user_min_level_vicinity = user.granularities[min_level].encrypted_vicinity
            group_user_min_level_location = group_user.granularities[min_level].encrypted_location
            group_user_min_level_vicinity = group_user.granularities[min_level].encrypted_vicinity

            # Look if agent position falls within vicinity
            gu_in_u = not {group_user_min_level_location.granule}.isdisjoint(user_min_level_vicinity.granules)
            u_in_gu = not {user_min_level_location.granule}.isdisjoint(group_user_min_level_vicinity.granules)

            if gu_in_u or u_in_gu:
                if min_level == user.max_level or min_level == group_user.max_level:
                    if gu_in_u and group_user not in user.proximate_users:
                        user.proximate_users.append(group_user)
                        await message_proximity_change(
                            is_vicinity_entry=True,
                            user_affected=user,
                            user_entered=group_user,
                            group=group,
                            data=data
                        )
                    if u_in_gu and user not in group_user.proximate_users:
                        group_user.proximate_users.append(user)
                        await message_proximity_change(
                            is_vicinity_entry=True,
                            user_affected=group_user,
                            user_entered=user,
                            group=group,
                            data=data
                        )
                else:
                    # TODO: Figure out if observers need this information
                    if min_level == len(user.granularities) - 1:
                        await user.websocket.send(MsgLSUserLevelIncrease(
                            to_level=min_level + 1
                        ).to_json())
                    if min_level == len(group_user.granularities) - 1:
                        await group_user.websocket.send(MsgLSUserLevelIncrease(
                            to_level=min_level + 1
                        ).to_json())

            if not gu_in_u and group_user in user.proximate_users:
                user.proximate_users.remove(group_user)
                await message_proximity_change(
                    is_vicinity_entry=False,
                    user_affected=user,
                    user_entered=group_user,
                    group=group,
                    data=data
                )
            if not u_in_gu and user in group_user.proximate_users:
                group_user.proximate_users.remove(user)
                await message_proximity_change(
                    is_vicinity_entry=False,
                    user_affected=group_user,
                    user_entered=user,
                    group=group,
                    data=data
                )
