from flask import Flask, json
import requests
import os
import mock_car
from flask_cors import CORS, cross_origin

TEMPORAL_CLOAKING_URL = os.getenv('TEMPORAL_CLOAKING_URL')

api = Flask(__name__)
cors = CORS(api)

id_of_car_running=0

@api.route('/')
def send_car_data():
  return "temporal_client"

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  response = requests.get(TEMPORAL_CLOAKING_URL + '/health')
  status = response.json()['status']
  if status == "ok":
    try:
      mock_car.test_connection()
      return json.dumps({ "status": "ok" })
    except:
      return json.dumps({ "status": "unhealthy" })
  return json.dumps({ "status": "unhealthy" })

# Call this route to tell the mocked client to start attaching
# to one of the cars driving in Carla
# NOTE: This is unclean and not following the REST pattern
@api.route('/start', methods=['GET'])
@cross_origin() # This is a route intended to be consumed by web frontends. TODO: Don't use wildcard cors
def get_start():
  id_of_car_running = mock_car.start_driving(service_query_interval=5)
  return json.dumps("simulation started ( Carla-" + str(id_of_car_running) + " running )")

# Call this route to tell the mocked client to stop the simulation
# NOTE: This is unclean and not following the REST pattern
@api.route('/stop', methods=['GET'])
@cross_origin() # This is a route intended to be consumed by web frontends. TODO: Don't use wildcard cors
def get_stop():
  mock_car.stop_all()
  return json.dumps({ "msg": "simulation stopped" })


if __name__ == '__main__':
    api.run(debug=True, host='0.0.0.0', port=5000)
