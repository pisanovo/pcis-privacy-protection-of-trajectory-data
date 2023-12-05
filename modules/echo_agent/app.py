import os
from flask import Flask, json
import requests

api = Flask(__name__)

LOCATION_SERVER_URL = os.getenv('LOCATION_SERVER_URL')

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  response = requests.get(LOCATION_SERVER_URL + '/health')
  status = response.json()['status']
  if status == 'ok':
    return json.dumps({ "status": "ok" })
  return json.dumps({ "status": "unhealthy" })

# Allows clients to make an anonymous requests
@api.route('/anonymous_resource', methods=['GET'])
def get_anonymous_resource():
  # TODO: Add actual request and don't just log
  return json.dumps({ "status": "ok" })

if __name__ == '__main__':
    api.run()