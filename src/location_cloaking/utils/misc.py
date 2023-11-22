from location_cloaking.client.model.data import VicinityCircleShape
from location_cloaking.model.data import Position


def point_in_rectangle(position: Position, x_min, x_max, y_min, y_max):
    return x_min <= position.x <= x_max and y_min <= position.y <= y_max


def grid_intersect_circle(position: Position,
                          vicinity_shape: VicinityCircleShape,
                          grid_seg_start: Position,
                          grid_seg_end: Position):
    # Check if the foot of the perpendicular form position (p) to the line falls between the segment (x1, y1) to
    # (x2, y2) and if the foot is at most radius (r) far from p. Otherwise, try to see if either (x1, y1) or
    # (x2, y2) are at most r far from p

    if grid_seg_start.x == grid_seg_end.x:
        x = grid_seg_start.x
        y = position.y
    else:
        x = position.x
        y = grid_seg_start.y

    is_foot_in_radius = (position.x - x) ** 2 + (position.y - y) ** 2 < vicinity_shape.radius ** 2
    is_foot_in_x_seg_range = grid_seg_start.x <= x <= grid_seg_end.x or grid_seg_end.x <= x <= grid_seg_start.x
    is_foot_in_y_seg_range = grid_seg_start.y <= y <= grid_seg_end.y or grid_seg_end.y <= y <= grid_seg_start.y
    is_in_segment = is_foot_in_x_seg_range if grid_seg_start.x != grid_seg_end.x else is_foot_in_y_seg_range
    is_seg_start_in_range = (position.x - grid_seg_start.x) ** 2 \
                            + (position.y - grid_seg_start.y) ** 2 < vicinity_shape.radius ** 2
    is_seg_end_in_range = (position.x - grid_seg_end.x) ** 2 \
                          + (position.y - grid_seg_end.y) ** 2 < vicinity_shape.radius ** 2

    if (is_in_segment and is_foot_in_radius) or is_seg_start_in_range or is_seg_end_in_range:
        return True
    else:
        return False
