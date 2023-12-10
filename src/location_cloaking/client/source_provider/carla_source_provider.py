import re
import time

import carla
from typing import List

from carla import World

from location_cloaking.client.source_provider.source_provider import SourceProvider
from location_cloaking.client.model.data import Position, ClientInstance, VicinityCircleShape, Policy, VicinityShape


class CarlaSourceProvider(SourceProvider):

    def __init__(self, source_instance_data: dict):
        from location_cloaking.config import CarlaConfig
        self._client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
        self._client.set_timeout(CarlaConfig.TIMEOUT)
        self._carla_world: World = self._client.get_world()
        self._carla_id = source_instance_data["id"]

    def get_latest_position(self) -> Position:
        # In synchronous mode getting actors might return nothing until a tick passed
        while len(self._carla_world.get_actors()) == 0:
            pass

        actor: carla.Actor = self._carla_world.get_actors().find(self._carla_id)
        actor_position: carla.Location = actor.get_location()

        return Position(actor_position.x, actor_position.y)

    @staticmethod
    def get_instances_from_cmd(cmd_input: List[str]) -> List[ClientInstance]:
        client_instances = []
        ids_processed = []

        for cmd_user_input in cmd_input:
            cmd_user_input = cmd_user_input[0]

            if "attach" in cmd_user_input:
                mode = "attach"
            else:
                raise ValueError("Unsupported client instance mode provided.")

            policy_max_lvl_match = re.search(r".*(policy_max_lvl:(\d*))", cmd_user_input).group(2)
            policy_max_lvl = int(policy_max_lvl_match)

            if policy_max_lvl < 0:
                raise ValueError("Invalid policy max lvl provided.")

            if "radius" in cmd_user_input:
                radius = re.search(r".*(radius:(\d*\.*\d+))", cmd_user_input).group(2)
                vicinity = VicinityCircleShape(radius=float(radius))
            else:
                raise ValueError(f"Unsupported {VicinityShape.__name__} found.")

            ids_match = re.search(r".*\sid:((,?(\d*-|\d*))*)", cmd_user_input).group(1)
            id_items = ids_match.split(",")
            ids = []

            for item in id_items:
                if "-" in item:
                    start, end = [int(i) for i in item.split("-")]

                    if start < end:
                        ids.extend(list(range(start, end + 1)))
                    else:
                        raise ValueError("Invalid id range provided.")
                else:
                    ids.append(int(item))

            if not set(ids_processed).isdisjoint(ids):
                raise ValueError("Found duplicate ids.")

            ids_processed.extend(ids)

            group_ids_match = re.search(r".*\sgroup_id:((,?(\d*-|\d*))*)", cmd_user_input).group(1)
            group_id_items = group_ids_match.split(",")
            group_ids = []

            for item in group_id_items:
                if "-" in item:
                    start, end = [int(i) for i in item.split("-")]

                    if start < end:
                        group_ids.extend(list(range(start, end + 1)))
                    else:
                        raise ValueError("Invalid id range provided.")
                else:
                    group_ids.append(int(item))

            for idx in ids:
                client_policy = Policy(max_level=policy_max_lvl, vicinity_shape=vicinity)
                client_instance = ClientInstance(
                    source_data={
                        "mode": mode,
                        "id": idx
                    },
                    alias=[
                        f"CARLA-id-{idx}"
                    ],
                    group_ids=list(set(group_ids)),
                    policy=client_policy
                )

                client_instances.append(client_instance)

        return client_instances

    @staticmethod
    def get_instances_from_json(json_input: dict) -> List[ClientInstance]:
        client_instances = []
        ids_processed = []

        for entry in json_input:
            mode = entry["mode"]

            if mode != "attach":
                raise ValueError("Unsupported client instance mode provided.")

            policy_max_lvl = entry["policy"]["max-level"]

            if policy_max_lvl < 0:
                raise ValueError("Invalid policy max lvl provided.")

            ids = []

            for item in entry["ids"]:
                if isinstance(item, int):
                    ids.append(item)
                else:
                    start, end = [int(i) for i in item.split("-")]

                    if start < end:
                        ids.extend(list(range(start, end + 1)))
                    else:
                        raise ValueError("Invalid id range provided.")

            if not set(ids_processed).isdisjoint(ids):
                raise ValueError("Found duplicate ids.")

            ids_processed.extend(ids)

            group_ids = []

            for item in entry["groups"]:
                if isinstance(item, int):
                    group_ids.append(item)
                else:
                    start, end = [int(i) for i in item.split("-")]

                    if start < end:
                        group_ids.extend(list(range(start, end + 1)))
                    else:
                        raise ValueError("Invalid group id range provided.")

            if entry["vicinity"]["type"] == VicinityCircleShape.__name__:
                radius = entry["vicinity"]["radius"]
                vicinity = VicinityCircleShape(radius=radius)
            else:
                raise ValueError(f"Unsupported {VicinityShape.__name__} found.")

            for idx in ids:
                client_policy = Policy(max_level=policy_max_lvl, vicinity_shape=vicinity)
                client_instance = ClientInstance(
                    source_data={
                        "mode": mode,
                        "id": idx
                    },
                    alias=[
                        f"CARLA-id-{idx}"
                    ],
                    group_ids=list(set(group_ids)),
                    policy=client_policy
                )

                client_instances.append(client_instance)

        return client_instances
