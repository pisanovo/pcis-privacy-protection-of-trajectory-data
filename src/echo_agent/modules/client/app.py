from flask import Flask, json
import requests
import os
import mock_car

ECHO_AGENT_URL = os.getenv('ECHO_AGENT_URL')

api = Flask(__name__)

# Keep track of the mock cars driving around
mock_car_intervals = []

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  response = requests.get(ECHO_AGENT_URL + '/health')
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
def get_start():
  mock_car_intervals.append(mock_car.start_driving(service_query_interval=15))
  return json.dumps({ "msg": "simulation started (" + str(len(mock_car_intervals)) + " running)" })

# Call this route to tell the mocked client to stop the simulation
# NOTE: This is unclean and not following the REST pattern
@api.route('/stop', methods=['GET'])
def get_stop():
  for interval in mock_car_intervals:
    interval.cancel()
  number_of_intervals = len(mock_car_intervals)
  mock_car_intervals.clear()
  return json.dumps({ "msg": str(number_of_intervals) + " simulations stopped" })


if __name__ == '__main__':
    api.run()
