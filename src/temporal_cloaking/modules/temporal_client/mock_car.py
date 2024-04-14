import carla
from flask import Flask, json
import random
import time
import threading
import requests
import os

CARLA_URL = str(os.getenv('CARLA_URL'))
CARLA_PORT = int(os.getenv('CARLA_PORT'))
TEMPORAL_CLOAKING_URL = str(os.getenv('TEMPORAL_CLOAKING_URL'))

# Helpers
def set_interval(func, sec):
  def func_wrapper():
      set_interval(func, sec) 
      func()  
  t = threading.Timer(sec, func_wrapper)
  t.start()
  return t

# Returns true if actors are available on the world in time
def wait_for_actors(world, retry_count = 10):
  while retry_count > 0:
      if len(world.get_actors()) > 0:
          break
      else:
          time.sleep(1.0)

  if retry_count == 0 and len(world.get_actors()) == 0:
      raise ValueError('Actors not populated in time')

  return True

# Test the connection to the Carla server
# and check if cars are driving
# Returns true, if connected, otherwise raises an error
def test_connection():
  client = carla.Client(CARLA_URL, CARLA_PORT)
  world = client.get_world()
  return wait_for_actors(world)

# The main function of this script.
# It attaches to one of the simulated cars in Carla
# and regularly queries the location service via temporal_cloaking
# Returns the newly picked car's id
# NOTE: It will make sure to only attach one car at a time
pre_picked_vehicle_id = ""
ego_vehicle=None
picked_vehicle_interval = None
def start_driving(service_query_interval=5):
  global pre_picked_vehicle_id, ego_vehicle, picked_vehicle_interval
  # 0.) Connect to the client and retrieve the world object
  client = carla.Client(CARLA_URL, CARLA_PORT)
  world = client.get_world()

  # 1.) Wait for actors to become available (will raise an error if it fails)
  wait_for_actors(world)

  # 2.) Get a random car from the ones driving around 
  all_vehicles = world.get_actors().filter('*vehicle*')
  ego_vehicle = None
  while ego_vehicle == None or ego_vehicle.id==pre_picked_vehicle_id:
    ego_vehicle = random.choice(list(all_vehicles))
  pre_picked_vehicle_id = ego_vehicle.id


  print('Picked a vehicle. Start tracking...')
  if picked_vehicle_interval==None:
    picked_vehicle_interval = set_interval(log_location, service_query_interval)
  return ego_vehicle.id

# Send cars' data to temporal_cloaking to execute the algorithm
def log_location():
  client = carla.Client(CARLA_URL, CARLA_PORT)
  world = client.get_world()

  wait_for_actors(world)

  all_vehicles = world.get_actors().filter('*vehicle*')

  # pass all vehicles' info to temporal_cloaking (the trusted party)
  for vehicle in all_vehicles:
    location = vehicle.get_location()
    geo_location = world.get_map().transform_to_geolocation(location)
    if vehicle.id != ego_vehicle.id:
      params = {
            "id": vehicle.id,
            "x": geo_location.longitude,
            "y": geo_location.latitude,
            "if_ego": 0,
            "service_name": 'service'
            }
      requests.get(
        'http://temporal_cloaking:5000' + '/anonymous_resource',
        params=params)
    else:
      params = {
            "id": vehicle.id,
            "x": geo_location.longitude,
            "y": geo_location.latitude,
            "if_ego": 1,
            "service_name": 'service'
            }
      requests.get(
        'http://temporal_cloaking:5000' + '/anonymous_resource',
        params=params)
  # end of all vehicles' info
  params = {
            "id": "end",
            "x": 0,
            "y": 0,
            "if_ego": 0,
            "service_name": 'service'
        }
  requests.get(
        'http://temporal_cloaking:5000' + '/anonymous_resource',
        params=params)
  return str("car info")


# Stops all simulated cars
# (cars in carla will continue to drive though,
# this just cancels the attachment to the cars)
def stop_all():
  global picked_vehicle_interval
  #picked_vehicle_interval.cancel()
