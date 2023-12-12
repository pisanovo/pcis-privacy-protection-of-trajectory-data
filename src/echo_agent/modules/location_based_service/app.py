from flask import Flask, json, request

api = Flask(__name__)

logs = []

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
  location = request.args.get('location')
  logs.append(location)
  return json.dumps({ "status": "ok" })

# This Route tells the visualization tool what information the
# location_based_service currently knows so that it can be visualized.
# In reality the location based service would obviously do something
# useful and for example call other microservices.
@api.route('/visualization_info', methods=['GET'])
def get_visualization_info():
   return json.dumps({ "logs": logs })


if __name__ == '__main__':
    api.run()