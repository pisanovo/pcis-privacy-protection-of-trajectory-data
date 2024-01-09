import os
import time

NUMBER_OF_DUMMIES = int(os.getenv('NUMBER_OF_DUMMIES'))

# Returns the locations of N dummies for a user.
# Then moves all dummies one step forward.
def get_dummies_for_user(user_id):
  # 1. Load user dummies from storage. If user has none, assign some.
  
  # 2. Collect current locations from each dummy. 
  dummies = get_dummies_from_db(user_id)
  current_locations = []
  for dummy in dummies:
    current_node_id = dummy['Curr_Node']
    current_node = dummy['Node_List'][current_node_id]
    current_locations.append(current_node)

  # 3. Move each dummy one node forward.
  for dummy in dummies:
    move_dummy_in_db(dummy['D_no'])

  # 4. Return result
  return current_locations


# Returns all dummies for a given user from the db
def get_dummies_from_db(user_id):
  # TODO: Implement DB access
  dummies = []

  # First, load dummies already assigned to user
  for dummy in mock_db:
    if dummy['Assigned_User'] == user_id:
      dummies.append(dummy)
  
  # Then, assign new dummies until threshold is reached
  for dummy in mock_db:
    if len(dummies) >= NUMBER_OF_DUMMIES:
      # user_id has enough dummies, cancel
      break

    if dummy['Assigned_User'] == None:
      dummies.append(dummy)
      dummy['Assigned_User'] == user_id

  return dummies

# Moves the current node of a dummy to the next node
# unless dummy has already reached end of its node list
def move_dummy_in_db(dummy_id):
  # TODO: Implement DB access
  for dummy in mock_db:
    if dummy['D_no'] == dummy_id and dummy['Curr_Node'] < dummy['No_of_Nodes'] - 1:
        dummy['Curr_Node'] += 1
  return

mock_db = [
    {
        "D_no": 0, # ID
        "Birth_Date": time.time(), # Created just now
        "No_of_Nodes": 3, # Length of Node_List
        "Assigned_User": None, # Can be assigned
        "Curr_Node": 0, 
        "SP_List": ["service"],
        "Node_List": [
            {"x":48.73460047395676,"y":9.112501862753065},
            {"x":48.73535788549441,"y":9.113227410029173},
            {"x":48.73556159973353,"y":9.11221444335842},
        ]
    },
    {
        "D_no": 1, # ID
        "Birth_Date": time.time(), # Created just now
        "No_of_Nodes": 3, # Length of Node_List
        "Assigned_User": None, # Can be assigned
        "Curr_Node": 0, 
        "SP_List": ["service"],
        "Node_List": [
            {"x":48.73460047395676,"y":9.112501862753065},
            {"x":48.73535788549441,"y":9.113227410029173},
            {"x":48.73556159973353,"y":9.11221444335842},
        ]
    },
    {
        "D_no": 2, # ID
        "Birth_Date": time.time(), # Created just now
        "No_of_Nodes": 3, # Length of Node_List
        "Assigned_User": None, # Can be assigned
        "Curr_Node": 0, 
        "SP_List": ["service"],
        "Node_List": [
            {"x":48.73460047395676,"y":9.112501862753065},
            {"x":48.73535788549441,"y":9.113227410029173},
            {"x":48.73556159973353,"y":9.11221444335842},
        ]
    },
]