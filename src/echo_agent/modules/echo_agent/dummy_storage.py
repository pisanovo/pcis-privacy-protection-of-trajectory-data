import os
from copy import deepcopy
from flask import json
import pickle
from set_interval import set_interval

NUMBER_OF_DUMMIES = int(os.getenv('NUMBER_OF_DUMMIES'))

# Returns the locations of N dummies for a user.
# Then moves all dummies one step forward.
def get_dummies_for_user(user_id):
  # 1. Load user dummies from storage. If user has none, assign some.
  dummies = get_dummies_from_db(user_id)
  
  # 2. Collect current locations from each dummy. 
  current_locations = []
  for dummy in dummies:
    current_node_index = dummy.Curr_Node
    current_node_id = dummy.Node_List[current_node_index]
    current_node = get_node(current_node_id)
    current_locations.append(current_node)

  # 3. Move each dummy one node forward.
  for dummy in dummies:
    move_dummy_in_db(dummy.D_No)

  # 4. Return result
  return current_locations

# Insert a node into the db
def insert_node(node):
   mock_db['nodes'].append(node)

# Insert a dummy into the db
def insert_dummy(dummy):
   mock_db['dummies'].append(dummy)

# Returns the specified node
def get_node(node_id):
    for node in mock_db["nodes"]:
        if node.Node_Id == node_id:
            return node
    return None

# Returns a specific dummy
def get_user_movement(dummy_id):
    for movement in mock_db["dummies"]:
        if movement.D_No == dummy_id:
            return movement
    return None

# Returns all dummies for a given user from the db
def get_dummies_from_db(user_id):
  # TODO: Implement DB access
  dummies = []

  # First, load dummies already assigned to user
  for dummy in mock_db["dummies"]:
    if dummy.Assigned_User == user_id:
      dummies.append(dummy)
  
  # Then, assign new dummies until threshold is reached
  for dummy in mock_db["dummies"]:
    if len(dummies) >= NUMBER_OF_DUMMIES:
      # user_id has enough dummies, cancel
      break

    if dummy.Assigned_User == None:
      dummies.append(dummy)
      dummy.Assigned_User = user_id

  return dummies

# Moves the current node of a dummy to the next node
# unless dummy has already reached end of its node list
def move_dummy_in_db(dummy_id):
  # TODO: Implement DB access
  for dummy in mock_db["dummies"]:
    if dummy.D_No == dummy_id and dummy.Curr_Node < dummy.No_of_Nodes - 1:
        dummy.Curr_Node += 1
  return


# Dumps a list of all dummies as json
def dump_dummies_json():
    dump = []
    # Populate node lists and prepare for json dumping (need to be dicts not 
    # instances of User_Movement)
    for dummy in mock_db["dummies"]:
        # Convert to dict so that we can json dump it
        dummy_dict = deepcopy(dummy.__dict__)
        # Populate and conver nodes
        Node_List_Populated = []
        for node_id in dummy_dict['Node_List']:
            node = get_node(node_id)
            Node_List_Populated.append(node.__dict__)
        dummy_dict['Node_List'] = Node_List_Populated
        dump.append(dummy_dict)
    return json.dumps(dump)

#########################
# Create a mock database
# in the RAM
##########################

mock_db = {
   "nodes": [],
   "dummies": []
}


#######################
# Persist the database
#######################

# Read the path to the storage volume from the environment
STORAGE_PATH = os.getenv('STORAGE_PATH')
PREFIX = "dummy_storage_"
NODES_FILE = os.path.join(STORAGE_PATH, PREFIX + "nodes.txt")
DUMMIES_FILE = os.path.join(STORAGE_PATH, PREFIX + "dummies.txt")

# Persist the database in a file
def write_db_to_file():
  # Write nodes
  nodes_file = open(NODES_FILE, "wb") 
  pickle.dump(mock_db["nodes"], nodes_file) 
  nodes_file.close() 
  # Write dummies
  dummies_file = open(DUMMIES_FILE, "wb")
  pickle.dump(mock_db["dummies"], dummies_file)
  dummies_file.close()

# Read the database from a file
def read_db_from_file():  
  # read nodes
  if os.path.exists(NODES_FILE):
    with open(NODES_FILE, 'rb') as handle: 
        node_data = handle.read()
    mock_db["nodes"] = pickle.loads(node_data) 

  # read dummies
  if os.path.exists(DUMMIES_FILE):
    with open(DUMMIES_FILE, 'rb') as handle: 
        dummies_data = handle.read()
    mock_db["dummies"] = pickle.loads(dummies_data) 

# Initially, read db file
read_db_from_file()

# Then start writing the db to file every 30 seconds until programm ends
set_interval(write_db_to_file, 30)
