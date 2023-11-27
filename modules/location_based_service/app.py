from flask import Flask, json

api = Flask(__name__)

@api.route('/hello', methods=['GET'])
def get_hello():
  return json.dumps({"msg": "Hello, here is the location based service. "})

if __name__ == '__main__':
    api.run()