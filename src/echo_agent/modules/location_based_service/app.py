from flask import Flask, json

api = Flask(__name__)

# Healthcheck. Responds with { "status": "ok" } if it, and all 
# services down the line are ok.
@api.route('/health', methods=['GET'])
def get_health():
  return json.dumps({ "status": "ok" })

if __name__ == '__main__':
    api.run()