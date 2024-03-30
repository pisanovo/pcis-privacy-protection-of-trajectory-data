# Location cloaking algorithm

Implementation based on the algorithm described in the [paper by Šikšnys et al](https://doi.org/10.1109/MDM.2010.43).

## Structure

IMG

The location cloaking prototype consists of two modules:
1. The [client](./client), which corresponds to a set of cars driving around within the Carla simulator. Multiple client instances
   with non-overlapping vehicle IDs can be used.
   The client converts position and vicinity to granule(s) (cell) IDs and sends the information to the location server. 
2. The [location server (LS)](./location_server), a potentially non-trusted party which runs the location cloaking algorithm.
   It collection updates from the client(s) and checks whether any overlap between a vehicle x position granule and a
   vehicle y vicinity granule occurred. If so it tries to instruct both vehicles to increase their level or send
   a proximity enter message otherwise. It also publishes the received client information to the frontend for visualization.
## Tech Stack

All modules are python applications, and they communicate via websockets.

## Setup

The location cloaking setup expects the following:
1. An instance of the Carla simulator running, with cars randomly driving around in it.
2. Each module should be running.

Following order should be followed when starting the location cloaking modules:
> Assumes that Carla is running and the [traffic generation script](utils/map/generate_random_traffic.py) 
> is used to generate the required traffic.
1. Start the [location server](./location_server/server.py).
2. Start the [client](./client/client.py).

Optionally:
- Adjust the [client config file](./data/client_config.json) 

## Client config
Defined as an array of config objects with the following structure:

- `mode`: `attach` only, listens to updates from carla
- `ids` : list of any following formats (can be mixed):
  - `<start_id>-<end_id>` will listen to updates for all vehicles in range `[<start_id>,<end_id>]`
  - `<id0>,<id1>,<id2>,...` will listen to the set of ids specified
   - Important: If your array of config objects has length > 1 it is necessary that IDs **do not** overlap
- `group`: list of groups vehicles specified in `ids` will be part of. The algorithm will be executed for each
           group and members of a group will not receive proximity enter notificatins from vehicles outside of the
           group
- `policy`: contains fields:
  - `max_level`: the maximum privacy level for the vehicles specified in `ids
- `vicinity`: contains fields:
  - `type`: currently only supports `VicinityCircleShape`
  - `radius`: radius of the vicinity circle


## Communication

### Client-Server

`MsgUserLSGroupJoin`: Set of vehicles represented by the running client will join the group specified in the message.

`MsgUserLSGroupLeave`: Set of vehicles represented by the running client will leave the group specified in the message.

`MsgUserLSPolicyChange`: Instruct the location server about a change in policy max level.

`MsgUserLSIncUpd`: Per vehicle update including vehicle ID, the level used to map vicinity and position to granules (cells),
the new location as granule ID, the vicinity provided as a list of granule IDs. Algorithm implements the incremental update
extension where only changes to the vicinity are published, i.e., vicinity delete and insert cell IDs.

### Server-Observer/Client

`MsgLSUserProximityEnter`: Notifies vehicle about another vehicle entering its vicinity area (contains the other vehicle ID).

`MsgLSUserProximityLeave`: Notifies vehicle about another vehicle leaving its vicinity area (contains the other vehicle ID).

`MsgLSUserLevelIncrease`: Instructs the client to increase its level. Client will ignore message if level does not meet privacy
constraints.

`MsgLSObserverIncUpd`: Forwards client updates to the frontend.

`MsgLSObserverSync`: Forwards the entire algorithm state to the frontend for synchronization purposes.

`MsgLSObserverProximity`: Notifies the frontend about proximity enter and leave events.

#### Error messages 
`MsgErrorInvalidGroup`: Joining non-existing group.

`MsgErrorNotGroupMember`: Trying to send updates to the LS for a group the client has not joined yet.

`MsgErrorGroupAlreadyJoined`
