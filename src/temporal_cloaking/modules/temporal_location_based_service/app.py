from flask import Flask, json, request
from flask_cors import CORS, cross_origin
import time

api = Flask(__name__)
# Enable CORS for this app, because it will be consumed by a web app
cors = CORS(api)

history_logs = []
logs = []

class Grid:
   def __init__(self, lon_min, lon_max, lat_min, lat_max):
      self.lon_min = lon_min
      self.lon_max = lon_max
      self.lat_min = lat_min
      self.lat_max = lat_max

class LogItem:
  def __init__(self, lon_min, lon_max, lat_min, lat_max):
    self.grid = Grid(lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max).__dict__
    self.timestamp = time.time() * 1000.0 # ms

@api.route('/')
def Hello_word():
  return "temporal_location_based_service"

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  return json.dumps({ "status": "ok" })

# This Route logs incoming coordinates.
# In reality, this would be an actual service
# that gives a useful answer. For the purpose of the protoype
# logging an visualizing what a service would see is enough.
@api.route('/service', methods=['GET'])
def get_service():
  lon_min = float(request.args.get('lon_min'))
  lon_max = float(request.args.get('lon_max'))
  lat_min = float(request.args.get('lat_min'))
  lat_max = float(request.args.get('lat_max'))
  log_item = LogItem(lon_min=lon_min, lon_max=lon_max, lat_min=lat_min, lat_max=lat_max)
  history_logs.append(log_item.__dict__)
  logs.clear()
  logs.append(log_item.__dict__)
  return json.dumps({ "status": "ok" })

# This Route tells the visualization tool what information the
# location_based_service currently knows so that it can be visualized.
# In reality the location based service would obviously do something
# useful and for example call other microservices.
@api.route('/visualization_info', methods=['GET'])
@cross_origin() # This is a route intended to be consumed by web frontends. TODO: Don't use wildcard cors
def get_visualization_info():
   return json.dumps({ "logs": logs })

# This Route flushes the logs so you don't have to restart the service to restart
@api.route('/visualization_info', methods=['DELETE'])
def delete_visualization_info():
   logs.clear()
   return json.dumps({ "msg": "deleted logs successfully" })

if __name__ == '__main__':
    api.run(debug=True, host='0.0.0.0', port=5002)