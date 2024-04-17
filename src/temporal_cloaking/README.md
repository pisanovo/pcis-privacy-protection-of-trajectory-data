# Temporal Cloaking algorithm

This is a prototypical implementation of the algorithm described in the (https://dl.acm.org/doi/abs/10.1145/1066116.1189037).

## Structure

This prototype consists of three modules:
1. The [client](./modules/client), which corresponds to a car driving around in the city.
   It wants to call a location based service anonymously by calling the temporal_cloaking and temporal_cloaking will decide what information is disclosed. 
2. The [temporal_cloaking](./modules/temporal_cloaking/), which is the module where this algorithm is executed. 
   It is a trusted third party, that calls the location based service for the client, and then disclose a grid area for the client to achieve anonymity.
3. The [location_based_service](./modules/location_based_service/), which corresponds to a service the client wants to call. 
   For the purpose of this prototype, it's a mock, that doesn't do anything more than sending an "ok" for every request.
   Its purpose is to allow us to inspect what the calls from the client, which are anonymized, look from the services perspective.

## Tech Stack

All modules are flask based python applications. They communicate via REST calls and you can interact with them via REST calls, too.

## Setup

This algorithm expects the following things:
1. An instance of carla simulator running, with cars randomly driving around in it.
2. A mongo_db database to store the echo_agent's state in.
3. Each module to be run as a flask application.

**To run the application, we recommend using docker compose, as specified in the main [Readme.md](../../Readme.md).**

## API

### Client

> NOTE: The client does not actually drive the car.
> It instead attaches randomly to a car in carla that is already driving around. 
> This is necessary because driving a car is pretty complicated, so generating random traffic somewhere else
> is much simpler implementation wise. 
> In reality, there is no simulator. A real client and car would directly call the temporal_cloaking and not need the
> client module from this prototype.

`[GET]/health`:
    Returns ok if itself and all downstream services work by sending a health check through the application - client, temporal_cloaking, mongo_db, location_based_service.

`[GET]/start`:
    Attach to a car driving around in carla.

`[GET]/stop`:
    Cancels all attachments. The cars in the simulator will still be driving, but the client will stop following them and stop calling the temporal_cloaking.

### Temporal Cloaking

`[GET]/health`:
    Returns ok if itself and all downstream services work by sending a health check through the application
    - temporal_cloaking, mongo_db, location_based_service. Is called by the client's healthcheck.
    
`[GET]/anonymous_resource?id=<client id>&x=<client x coordinate>&y=<client y coordinate>&if_ego=<if client is ego>&service_name=service`:
    This is the route the client calls to reach the location based service anonymously. It passes all cars' info and the name of the service.
    However, as this is a prototype and only one service exists, the service name is always service.

`[POST]/getK?constraint_k=<number>`: 
    Set constraint k.


### Location Based Service

`[GET]/health`:
    Returns ok if itself is healthy. Is called by the temporal_cloaking's healthcheck, which is called by the client's healthcheck

`[GET]/service?lon_min=<x coordinate>&lon_max=<x coordinate>&lat_min=<y coordinate>&lat_max=<y coordinate`: 
    This is the mocked service the client wants to consume. It just returns okay for every call
    and logs the grid area so that we can inspect the data the location based service knows later.

`[GET]/visualization_info`:
    Dumps a list of everything the location based server knows about the clients, prepared for
    visualization.

`[DELETE]/visualization_info`:
    Deletes the list of everything the location based server knows about the clients.

> NOTE: The visualization_info is non-persistend. When the service restarts,
> all information will be gone. However, as it is not very important and because 
> the service is not likely to randomly restart very often, the prototype does not need
> log persistence here.
