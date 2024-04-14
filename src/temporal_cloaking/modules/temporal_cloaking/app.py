import math
import os
from flask import Flask, json, request, Response
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask_cors import CORS, cross_origin

constraint_k = 5
# store vehicles' info
class CarData:
    def __init__(self, id, x, y, if_ego):
        self.id = id
        self.x = x
        self.y = y
        self.if_ego = if_ego
cars_position = []
end_info_flag = 0

# longitude and latitude of the selected area
lon_min = 9.07962801
lat_min = 48.72741225
lat_max = 48.75670065
lat_dif = lat_max-lat_min
lon_dif = lat_dif/ math.cos((lat_min * math.pi) / 180)

# length of quadrant's longitude and latitude at each step
quadrant_lat=0
quadrant_lon=0
# current step's quadrant and previous step's quadrant at each step
cur_quadrant_lon_min=0
cur_quadrant_lat_min=0
cur_quadrant_lon_max=0
cur_quadrant_lat_max=0
prev_quadrant_lon_min=0
prev_quadrant_lat_min=0
prev_quadrant_lon_max=0
prev_quadrant_lat_max=0
# count the number of vehicles in the vicinity of the ego vehicle
vicinity_cnt = 0
# location of ego vehicle
ego_x = 0
ego_y = 0

active_agents = []

api = Flask(__name__)
cors = CORS(api)

# Get env variables
LOCATION_SERVER_URL = os.getenv('LOCATION_SERVER_URL')


@api.route('/')
def Hello_word():
  return "temporal_cloaking"

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  healthy = True

  # Test connection to location server
  location_server_response = requests.get(LOCATION_SERVER_URL + '/health')
  location_server_status = location_server_response.json()['status']
  healthy = healthy and (location_server_status == 'ok')
  if healthy:
    return json.dumps({ "status": "ok" })
  return json.dumps({ "status": "unhealthy" })

# Allows clients to make an anonymous requests
@api.route('/anonymous_resource', methods=['GET'])
def get_anonymous_resource():
  global cars_position, end_info_flag
  global lon_min, lat_min, lat_max, lat_dif, lon_dif
  global quadrant_lat, quadrant_lon
  global cur_quadrant_lon_min, cur_quadrant_lon_max, cur_quadrant_lat_min, cur_quadrant_lat_max, prev_quadrant_lon_min, prev_quadrant_lon_max, prev_quadrant_lat_min, prev_quadrant_lat_max
  global vicinity_cnt, ego_x, ego_y
  global active_agents
  # 0. Parse data
  # Parse all vehicles' info
  id = str(request.args.get('id'))
  if id != "end":
    if id not in active_agents:
      active_agents.append(id)
    else:
      active_agents.clear()
      active_agents.append(id)
      cars_position.clear()
    x = float(request.args.get('x'))
    y = float(request.args.get('y'))
    if_ego = int(request.args.get('if_ego'))
    service_name = request.args.get('service_name')
    new_carData = CarData(id, x, y, if_ego)
    cars_position.append(new_carData)
    return "just read info"
  else:
    eat_buffer=request.args.get('x')
    eat_buffer=request.args.get('y')
    eat_buffer=request.args.get('if_ego')
    eat_buffer=request.args.get('service_name')
    end_info_flag = 1
  #api.logger.info(cars_position[0].id)
  

  # 2. Execute the algorithm and call service (in our case, only one mocked one exists)
  if end_info_flag==1:
    end_info_flag = 0

    # the temporal_cloaking algorithm
    quadrant_lat = lat_dif
    quadrant_lon = lon_dif
    cur_quadrant_lon_min = lon_min
    cur_quadrant_lon_max = lon_min+quadrant_lon
    cur_quadrant_lat_min = lat_min
    cur_quadrant_lat_max = lat_min+quadrant_lat
    prev_quadrant_lon_min = lon_min
    prev_quadrant_lon_max = lon_min+quadrant_lon
    prev_quadrant_lat_min = lat_min
    prev_quadrant_lat_max = lat_min+quadrant_lat

    for step in range(8):
      vicinity_cnt = 0
      for carData in cars_position:
        if carData.if_ego==0:
          if carData.x >= cur_quadrant_lon_min and carData.x <= cur_quadrant_lon_max and carData.y >= cur_quadrant_lat_min and carData.y <= cur_quadrant_lat_max:
            vicinity_cnt = vicinity_cnt+1
        else:
          ego_x = carData.x
          ego_y = carData.y
          vicinity_cnt = vicinity_cnt+1

      # constraint k is fullfilled, the algorithm ends
      if vicinity_cnt<constraint_k:
        break

      # find out which sub quadrant ego vehicle is in
      quadrant_lat = quadrant_lat/2.000
      quadrant_lon = quadrant_lon/2.000
      if ego_x <= cur_quadrant_lon_min+quadrant_lon and ego_y <= cur_quadrant_lat_min+quadrant_lat:
          prev_quadrant_lon_max = cur_quadrant_lon_max
          cur_quadrant_lon_max = cur_quadrant_lon_min+quadrant_lon

          prev_quadrant_lat_max = cur_quadrant_lat_max
          cur_quadrant_lat_max = cur_quadrant_lat_min+quadrant_lat

          prev_quadrant_lon_min = cur_quadrant_lon_min
          prev_quadrant_lat_min = cur_quadrant_lat_min
      elif ego_x <= cur_quadrant_lon_min+quadrant_lon and ego_y >= cur_quadrant_lat_min+quadrant_lat:
          prev_quadrant_lon_max = cur_quadrant_lon_max
          cur_quadrant_lon_max = cur_quadrant_lon_min+quadrant_lon

          prev_quadrant_lat_min = cur_quadrant_lat_min
          cur_quadrant_lat_min = cur_quadrant_lat_min+quadrant_lat

          prev_quadrant_lon_min = cur_quadrant_lon_min
          prev_quadrant_lat_max = cur_quadrant_lat_max
      elif ego_x >= cur_quadrant_lon_min+quadrant_lon and ego_y <= cur_quadrant_lat_min+quadrant_lat:
          prev_quadrant_lon_min = cur_quadrant_lon_min
          cur_quadrant_lon_min = cur_quadrant_lon_min+quadrant_lon

          prev_quadrant_lat_max = cur_quadrant_lat_max
          cur_quadrant_lat_max = cur_quadrant_lat_min+quadrant_lat

          prev_quadrant_lon_max = cur_quadrant_lon_max
          prev_quadrant_lat_min = cur_quadrant_lat_min
      elif ego_x >= cur_quadrant_lon_min+quadrant_lon and ego_y >= cur_quadrant_lat_min+quadrant_lat:
          prev_quadrant_lon_min = cur_quadrant_lon_min
          cur_quadrant_lon_min = cur_quadrant_lon_min+quadrant_lon

          prev_quadrant_lat_min = cur_quadrant_lat_min
          cur_quadrant_lat_min = cur_quadrant_lat_min+quadrant_lat

          prev_quadrant_lon_max = cur_quadrant_lon_max
          prev_quadrant_lat_max = cur_quadrant_lat_max
                                
    # clear all saved vehicles' info
    cars_position.clear()

    # Call the service using result of the algorithm
    requests.get('http://temporal_location_based_service:5000' + '/service', 
                 params={'lon_min': prev_quadrant_lon_min, 'lon_max': prev_quadrant_lon_max, 'lat_min':prev_quadrant_lat_min, 'lat_max':prev_quadrant_lat_max})
    return json.dumps("algorithm successfully generated result")  
  #   # Forward real response, in this case, if service returned ok
  #   if response.ok:
  #     return json.dumps({ "status": "ok" })
  #   else:
  #     # The location service is mocked, so any error is misconfiguration / implementation / ... related
  #     return Response('{"status": "internal server error"}', status=500, mimetype='application/json')
  # # INFO: Here is where you would add more services. This prototype only needs one.
  # # Fallback, incase an unknown service_name was passed on
  # return Response('{"status": "invalid property service_name"}', status=401, mimetype='application/json')


# Get parameter constraint k
@api.route('/getk', methods=['GET','POST'])
@cross_origin() # This is a route intended to be consumed by web frontends. TODO: Don't use wildcard cors
def post_getK():
  global constraint_k
  constraint_k = int(request.args.get('constraint_k'))
  successful = 1
  if successful:
    return json.dumps("set constraint k succesfully to "+str(constraint_k))
  else:
    return json.dumps({"msg": "Setting constraint k failed"})

if __name__ == '__main__':
    api.run(debug=True, host='0.0.0.0', port=5001)
