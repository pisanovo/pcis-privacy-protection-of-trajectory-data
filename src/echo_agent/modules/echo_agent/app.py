import os
from flask import Flask, json, request, Response
import requests
import mysql.connector

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
echo_db = mysql.connector.connect(
   host=ECHO_DB_HOST,
   user=ECHO_DB_USER,
   password=ECHO_DB_PASSWORD
)

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  healthy = True
  # Test connection to db server
  healthy = healthy and echo_db.is_connected()

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
  # TODO: Anonymize and don't just pass through
  location = request.args.get('location') 
  service_name = request.args.get('service_name')
  if service_name == 'service':
    response = requests.get(LOCATION_SERVER_URL + '/service', params={'location': location})
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