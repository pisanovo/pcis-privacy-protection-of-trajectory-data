import os
from flask import Flask, json, request, Response
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dummy_generator import get_dummies_for_user


api = Flask(__name__)

# Get env variables
LOCATION_SERVER_URL = os.getenv('LOCATION_SERVER_URL')
ECHO_DB_HOST = os.getenv('ECHO_DB_HOST')
ECHO_DB_USER = os.getenv('ECHO_DB_USER')
ECHO_DB_PASSWORD_FILE = os.getenv('ECHO_DB_PASSWORD_FILE')

# Read secret files
f = open(ECHO_DB_PASSWORD_FILE,"r")
lines = f.readlines()
ECHO_DB_PASSWORD = lines[0]
f.close()

# Connect to mysql db
echo_db = MongoClient(ECHO_DB_HOST, 27017) # Default port

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  healthy = True
  # Test connection to db server
  try:
    echo_db.admin.command('ping')
  except ConnectionFailure:
      healthy = False

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
  # Parse real client location and user id
  x = float(request.args.get('x'))
  y = float(request.args.get('y')) 
  user_id = str(request.args.get('user_id'))
  # Parse desired service name (NOTE: In this prototype, only one service exists)
  service_name = request.args.get('service_name')
  # Get the locations of N dummies
  dummy_locations = get_dummies_for_user(user_id=user_id)
  if service_name == 'service':
    # Call the service for all the dummies, and once with the real location
    # NOTE: In reality, you should do this randomly, so the server cannot guess from order who is dummy
    response = requests.get(LOCATION_SERVER_URL + '/service', params={'x': x, 'y': y})
    for dummy_location in dummy_locations:
      requests.get(
        LOCATION_SERVER_URL + '/service',
        params={'x': dummy_location['x'], 'y': dummy_location['y']}
      )
    # Forward real response, in this case, if service returned ok
    if response.ok:
      return json.dumps({ "status": "ok" })
    else:
      # The location service is mocked, so any error is misconfiguration / implementation / ... related
      return Response('{"status": "internal server error"}', status=500, mimetype='application/json')
  # INFO: Here is where you would add more services. This prototype only needs one.
  # We do not pass the route directly, to avoid things like directory traversal vulnerabilities.
  return Response('{"status": "invalid property service_name"}', status=401, mimetype='application/json')

if __name__ == '__main__':
    api.run()
