from flask import Flask, json
import requests

api = Flask(__name__)

@api.route('/hello', methods=['GET'])
def get_hello():
  response = requests.get('http://location_based_service:5000/hello')
  msg = response.json()['msg']
  return json.dumps({"msg": "Hello, here is the echo agent. The location service sais " + msg})

if __name__ == '__main__':
    api.run()