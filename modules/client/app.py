from flask import Flask, json
import requests

api = Flask(__name__)

@api.route('/hello', methods=['GET'])
def get_hello():
  response = requests.get('http://echo_agent:5000/hello')
  msg = response.json()
  return json.dumps(msg)

if __name__ == '__main__':
    api.run()