from flask import Flask, json, request

api = Flask(__name__)

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
  # By default, log level is warning and higher.
  # We could change this, but this is only placeholder code for the 
  # actual visualization, and thus it's not worth it.
  api.logger.warning('SERVICE received location: ' + str(location))
  return json.dumps({ "status": "ok" })

if __name__ == '__main__':
    api.run()