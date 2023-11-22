from __future__ import annotations
from location_cloaking.client.source_provider.carla_source_provider import CarlaSourceProvider
from location_cloaking.client.source_provider.source_provider import SourceProvider
from location_cloaking.client.model.data import Position, Policy, VicinityShape, VicinityCircleShape
from location_cloaking.client.model.messages import MsgUserLSIncUpd
from location_cloaking.location_server.model.messages import MsgLSUserLevelIncrease
from location_cloaking.model.data import GranularityPlaneDimensions, GranularityLevel, UserLocation, UserVicinity, \
    EncryptedUserLocation, EncryptedUserVicinity
from location_cloaking.utils.misc import point_in_rectangle, grid_intersect_circle
import math


class LocationHandler:
    _last_position: Position
    _plane_dim: GranularityPlaneDimensions
    _policy: Policy
    _granularity_stack: list[GranularityLevel]
    _websocket: any

    def __init__(self, location_provider: SourceProvider, plane_dim: GranularityPlaneDimensions, policy: Policy,
                 user_id: int):
        self._location_provider: CarlaSourceProvider = location_provider
        self._last_position = self._location_provider.get_latest_position()
        self._plane_dim = plane_dim
        self._policy = policy
        self._granularity_stack = []
        self._old_granularity_stack = []
        self._user_id = user_id

    def _get_position_level_granule(self, level: int, position: Position):
        # If position is outside of granularity there is no granule to assign
        if position.x < self._plane_dim.x_min or position.x > self._plane_dim.x_max or \
                position.y < self._plane_dim.y_min or position.y > self._plane_dim.y_max:
            return None

        granule_level_width = self._plane_dim.width / math.pow(2, level + 1)
        granule_level_height = self._plane_dim.height / math.pow(2, level + 1)
        position_x_shifted = position.x + abs(
            self._plane_dim.x_min) if self._plane_dim.x_min < 0 else position.x - self._plane_dim.x_min
        position_y_shifted = position.y + abs(
            self._plane_dim.y_min) if self._plane_dim.y_min < 0 else position.y - self._plane_dim.y_min
        granule_column = min(math.floor(position_x_shifted / granule_level_width), int(math.pow(2, level + 1)))
        granule_row = min(math.floor(position_y_shifted / granule_level_height), int(math.pow(2, level + 1)))

        num_granules_upto_level = (4 / 3) * (math.pow(4, level) - 1)
        granule_id = num_granules_upto_level + math.pow(2, level + 1) * granule_row + granule_column

        return int(granule_id)

    def _get_vicinity_level_granules(self, level: int, position: Position, vicinity_shape: VicinityShape):
        granules = []

        if isinstance(vicinity_shape, VicinityCircleShape):
            granule_level_height = self._plane_dim.height / math.pow(2, level + 1)
            granule_level_width = self._plane_dim.width / math.pow(2, level + 1)

            # Get the bounding box of the circle
            circle_x_min = position.x - vicinity_shape.radius
            circle_x_max = position.x + vicinity_shape.radius
            circle_y_min = position.y - vicinity_shape.radius
            circle_y_max = position.y + vicinity_shape.radius

            # Get the granularity area where we need to iterate over the granules and check if there is an intersection
            # scan_y_min is the first granularity grid line on the y-axis above the circle, scan_y_max -"- below...
            scan_y_min = max(self._plane_dim.y_min, self._plane_dim.y_min + granule_level_height *
                             (math.floor((circle_y_min - self._plane_dim.y_min) / granule_level_height)))
            scan_y_max = min(self._plane_dim.y_max, self._plane_dim.y_max - granule_level_height *
                             (math.floor((self._plane_dim.y_max - circle_y_max) / granule_level_height)))
            scan_x_min = max(self._plane_dim.x_min, self._plane_dim.x_min + granule_level_width *
                             (math.floor((circle_x_min - self._plane_dim.x_min) / granule_level_width)))
            scan_x_max = min(self._plane_dim.x_max, self._plane_dim.x_max - granule_level_width *
                             (math.floor((self._plane_dim.x_max - circle_x_max) / granule_level_width)))

            # Start scanning over the relevant granularity area
            x = scan_x_min
            while x < scan_x_max:
                y = scan_y_min
                while y < scan_y_max:
                    # https://stackoverflow.com/a/402019
                    granule_p_a = Position(x, y)
                    granule_p_b = Position(x + granule_level_width, y)
                    granule_p_c = Position(x + granule_level_width, y + granule_level_height)
                    granule_p_d = Position(x, y + granule_level_height)
                    if point_in_rectangle(position, x, x + granule_level_width, y, y + granule_level_height) or \
                            grid_intersect_circle(position, vicinity_shape, granule_p_a, granule_p_b) or \
                            grid_intersect_circle(position, vicinity_shape, granule_p_b, granule_p_c) or \
                            grid_intersect_circle(position, vicinity_shape, granule_p_c, granule_p_d) or \
                            grid_intersect_circle(position, vicinity_shape, granule_p_d, granule_p_a):

                        granule_center_point = Position(x=x + (granule_level_width / 2),
                                                        y=y + (granule_level_height / 2))
                        granule = self._get_position_level_granule(level, granule_center_point)

                        if granule is not None:
                            granules.append(granule)

                    y += granule_level_height
                x += granule_level_width

        return granules

    def _map_location_to_granularity(self, level: int, position: Position):
        granule_location = self._get_position_level_granule(level, position)
        granules_vicinity = self._get_vicinity_level_granules(level, position, self._policy.vicinity_shape)
        return granule_location, granules_vicinity

    async def _push_and_send(self, position: Position, websocket):
        new_position_granule, new_vicinity_granules = self._map_location_to_granularity(len(self._granularity_stack), position)
        self._granularity_stack.append(GranularityLevel(
                location=UserLocation(int(new_position_granule)),
                vicinity=UserVicinity(new_vicinity_granules)
            )
        )

        if len(self._granularity_stack) <= len(self._old_granularity_stack):
            old_vicinity_granules = self._old_granularity_stack[len(self._granularity_stack) - 1].vicinity.granules
            vicinity_granules_del = [gl for gl in old_vicinity_granules if gl not in new_vicinity_granules]
            vicinity_granules_ins = [gl for gl in new_vicinity_granules if gl not in old_vicinity_granules]
        else:
            vicinity_granules_del = []
            vicinity_granules_ins = new_vicinity_granules

        if len(vicinity_granules_del) == 0 and len(vicinity_granules_ins) == 0:
            return

        if self._user_id == 3:
            print(len(self._granularity_stack) - 1, vicinity_granules_del, vicinity_granules_ins)

        await websocket.send(MsgUserLSIncUpd(
            user_id=self._user_id,
            level=len(self._granularity_stack) - 1,
            new_location=EncryptedUserLocation(granule=new_position_granule),
            vicinity_delete=EncryptedUserVicinity(granules=vicinity_granules_del),
            vicinity_insert=EncryptedUserVicinity(granules=vicinity_granules_ins),
            vicinity_shape=self._policy.vicinity_shape
        ).to_json())

    def _has_top_gs_changed(self, position):
        new_position_granule, new_vicinity_granules = self._map_location_to_granularity(len(self._granularity_stack) - 1, position)
        old_position_granule = self._granularity_stack[len(self._granularity_stack) - 1].location.granule
        old_vicinity_granules = self._granularity_stack[len(self._granularity_stack) - 1].vicinity.granules

        return old_position_granule != new_position_granule or old_vicinity_granules != new_vicinity_granules

    async def on_location_change(self, position: Position, websocket):
        was_popped = False

        while len(self._granularity_stack) > 0 and self._has_top_gs_changed(position):
            self._granularity_stack.pop()
            was_popped = True

        if was_popped or len(self._granularity_stack) == 0:
            await self._push_and_send(position, websocket)

    async def run_update(self, websocket):
        new_position = self._location_provider.get_latest_position()
        if not self._last_position or new_position.x != self._last_position.x or new_position.y != self._last_position.y:
            self._old_granularity_stack = self._granularity_stack.copy()
            await self.on_location_change(new_position, websocket)

    async def on_message_received(self, m_lvl_inc: MsgLSUserLevelIncrease, websocket):
        new_position = self._location_provider.get_latest_position()
        gs_len = len(self._granularity_stack)
        self._old_granularity_stack = self._granularity_stack.copy()
        while gs_len <= m_lvl_inc.to_level and gs_len <= self._policy.max_level:
            await self._push_and_send(new_position, websocket)
            gs_len = len(self._granularity_stack)
