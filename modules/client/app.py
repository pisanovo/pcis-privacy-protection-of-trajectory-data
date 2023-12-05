from flask import Flask, json
import requests

import mock_car

api = Flask(__name__)

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  response = requests.get('http://echo_agent:5000/health')
  status = response.json()['status']
  if status == "ok":
    return json.dumps({ "status": "ok" })
  return json.dumps({ "status": "unhealthy" })

# Call this route to tell the mocked client to start attaching
# to one of the cars driving in Carla
# NOTE: This is unclean and not following the REST pattern
@api.route('/start', methods=['GET'])
def get_start():
  mock_car.start_driving(service_query_interval=5)
  return json.dumps({ "msg": "simulation started" })


if __name__ == '__main__':
    api.run()
