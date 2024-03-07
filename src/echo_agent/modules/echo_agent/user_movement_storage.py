import time
import random
from copy import deepcopy
from flask import json

# TODO: As soon as we use a real database, ids can be generate by it
ID_COUNTER = {
    "count": 0
}
def get_unique_movement_id():
    ID_COUNTER["count"] = ID_COUNTER["count"] + 1
    return "movement-" + str(ID_COUNTER["count"])

class User_Movement:
    def __init__(self, R_No):
        self.R_No = R_No
        self.Birth_Date = time.time()
        self.No_of_Nodes = 0
        self.Used_Freq = 0
        self.Node_List = []
    
    def insert_node(self, node):
        self.Node_List.append(node.Node_Id)
        self.No_of_Nodes = self.No_of_Nodes + 1
        node.set_parent(self.R_No)

class Location:
    def __init__(self, x, y):
        self.Node_Id = get_unique_movement_id()
        self.x = x
        self.y = y
        self.parent_id = None # Link Nodes to parents so that, when searching over all nodes, its easy to find parent for each node

    def set_parent(self, new_parent_id):
        self.parent_id = new_parent_id

# Adds a user location to a movement in storage
def insert_user_location(user_id, x, y):
    # 0. Find current movement for user in storage. 
    #    If none exists, create a new one.
    movement_id = user_id_movement_id_map.get(user_id)     
    if movement_id == None: 
        # Generate new id
        movement_id = get_unique_movement_id()
        # Add it to map
        user_id_movement_id_map[user_id] = movement_id
        # Add new entry into db
        new_movement = User_Movement(R_No = movement_id)
        mock_db["user_movements"].append(new_movement)        

    # 1. Insert new location node
    new_location_node = Location(x=x, y=y)
    mock_db["nodes"].append(new_location_node)
    get_user_movement(movement_id).insert_node(new_location_node)

    return

# Returns the specified node
def get_node(node_id):
    for node in mock_db["nodes"]:
        if node.Node_Id == node_id:
            return node
    return None

# Returns a specific user movement
def get_user_movement(user_movement_id):
    for movement in mock_db["user_movements"]:
        if movement.R_No == user_movement_id:
            return movement
    return None

# Get random user movement
def get_random_user_movement():
    return random.choice(mock_db["user_movements"])

# Finds neighbour nodes close to a specified node.
# A neighbour node is a node that is close, but
# not from the same user movement.
def search_neighbours(node_id, distance_threshold = 0.001): # 0.001 latitude/longitude difference corresponds to 111 meters
    search_node = get_node(node_id) 
    result_list = []
    for node in mock_db["nodes"]:
        # Don't compare to self
        if node.Node_Id == search_node.Node_Id:
            continue
        # Don't compare to same user movement
        if node.parent_id == search_node.parent_id:
            continue
        # Is node close enough?
        delta_x = abs(node.x - search_node.x)
        delta_y = abs(node.y - search_node.y)
        if delta_x > distance_threshold and delta_y > distance_threshold:
            continue
        # Node is a suitable candidate! Add to results
        result_list.append(node)
    return result_list

# Dumps a list of all user movements
# as json
def dump_user_movements_json():
    dump = []
    # Populate node lists and prepare for json dumping (need to be dicts not 
    # instances of User_Movement)
    for movement in mock_db["user_movements"]:
        # Convert to dict so that we can json dump it
        movement_dict = deepcopy(movement.__dict__)
        # Populate and conver nodes
        Node_List_Populated = []
        for node_id in movement_dict['Node_List']:
            node = get_node(node_id)
            Node_List_Populated.append(node.__dict__)
        movement_dict['Node_List'] = Node_List_Populated
        dump.append(movement_dict)
    return json.dumps(dump)
    

# Records which movement every user is currently
# writing to
user_id_movement_id_map = {}

# Mock DB of user movements
mock_db = {
    "nodes": [],
    "user_movements": [],
}