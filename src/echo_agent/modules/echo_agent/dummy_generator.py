import time
import user_movement_storage
import dummy_storage
from copy import deepcopy

# TODO: As soon as we use a real database, ids can be generate by it
ID_COUNTER = {
    "count": 0
}
def get_unique_dummy_id():
    ID_COUNTER["count"] = ID_COUNTER["count"] + 1
    return "dummy-" + str(ID_COUNTER["count"])

class Dummy:
    def __init__(self, D_No):
        self.D_No = D_No
        self.Birth_Date = time.time()
        self.No_of_Nodes = 0
        self.Assigned_User = None
        self.Used_Freq = 0
        # ignore SP_List for now, because the prototype only knows of one service
        self.Curr_Node = 0
        self.Node_List = []
    
    def insert_node(self, node):
        self.Node_List.append(node.Node_Id)
        self.No_of_Nodes = self.No_of_Nodes + 1
        node.set_parent(self.D_No)

# Generates one dummy and adds it to the dummy storage
# Returns true if generation was successful and false if not
def generate_dummy(min_node_count, max_node_count, nb_range):
    # Initialize empty Node_List and current_node_id
    dummy_node_ids = []
    current_node_id = None

    # Get a random route from User Movement Storage
    selected_user_movement = user_movement_storage.get_random_user_movement()
    # Set first node of selected route for start node of dummy
    dummy_node_ids.append(selected_user_movement.Node_List[0])
    current_node_id = dummy_node_ids[0]

    # Stores the steps that happened
    trace = []


    # The number of Nodes in Dummy is less than maximum number of nodes?
    while len(dummy_node_ids) < max_node_count:
        # YES: The Current Node of selected route is a final node?
        next_node_id_index = selected_user_movement.Node_List.index(current_node_id) + 1
        if next_node_id_index >= selected_user_movement.No_of_Nodes:
            trace.append('Node ' + current_node_id + ' was final node')
            # YES: The number of nodes in dummy is greater than minimum number of nodes?
            if len(dummy_node_ids) >= min_node_count:
                trace.append('Finished generation because min length is reached while on a final node')
                # YES: Moving to storing the dummy
                break
            # NO: Change the current node field into neighbouring node of adjoining route
            neighbours = user_movement_storage.search_neighbours(node_id=current_node_id, distance_threshold=nb_range)
            next_neighbouring_node = select_unused_neighbour(current_node_ids_list=dummy_node_ids, search_result_list=neighbours)
            if not next_neighbouring_node == None:
                current_node_id = next_neighbouring_node.Node_Id
                trace.append('Moved to neighbouring node ' + current_node_id + ' after reaching a final node')
                selected_user_movement = user_movement_storage.get_user_movement(user_movement_id=next_neighbouring_node.parent_id)
            else:
                # Couldn't find a node, dummy generation failed
                return False
        else:
            # NO: Add the current node of selected route to dummy
            trace.append('Adding node ' + current_node_id + ' to dummy')
            dummy_node_ids.append(current_node_id)
            # Is there any neighbouring node with current node of 
            # selected route in user movement storage?
            neighbours = user_movement_storage.search_neighbours(node_id=current_node_id, distance_threshold=nb_range)
            next_neighbouring_node = select_unused_neighbour(current_node_ids_list=dummy_node_ids, search_result_list=neighbours)
            if not next_neighbouring_node == None:
                current_node_id = next_neighbouring_node.Node_Id
                trace.append('Moving to neighbouring node ' + current_node_id + ' randomly')
                selected_user_movement = user_movement_storage.get_user_movement(user_movement_id=next_neighbouring_node.parent_id)
            else:
                # NO: Couldn't find a node, change the current node field into next node of selected route
                current_node_id = selected_user_movement.Node_List[next_node_id_index]
                trace.append('No neighbour found randomly, so moving to next node ' + current_node_id + ' of current movement')

    # NO: Store new dummy to dummy storage

    # 1. Create new nodes
    new_nodes = []
    for node_id in dummy_node_ids:
        new_node = deepcopy(user_movement_storage.get_node(node_id))
        dummy_storage.insert_node(new_node)
        new_nodes.append(new_node)
    # 2. Create a new dummy
    new_dummy = Dummy(get_unique_dummy_id())
    new_dummy.trace = ' -> '.join(trace)
    dummy_storage.insert_dummy(new_dummy)
    # 3. Connect nodes to dummy
    for node in new_nodes:
        new_dummy.insert_node(node)
        
    return True


# Helper function to pick a neighbour from search results that
# is not yet in the list of nodes
# Bot lists may be empty, but cannot be undefined.
# current_node_list should be a list of ids
# search_result_list should be a list of nodes
def select_unused_neighbour(current_node_ids_list, search_result_list):
    # pick first element that isn't in current_node_list
    for node in search_result_list:
        if node.Node_Id in current_node_ids_list:
            continue
        else:
            return node
    # If none were found, return nothing
    return None
