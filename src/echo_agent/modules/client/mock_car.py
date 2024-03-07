import carla
import random
import time
import threading
import requests
import os

CARLA_URL = str(os.getenv('CARLA_URL'))
CARLA_PORT = int(os.getenv('CARLA_PORT'))
ECHO_AGENT_URL = str(os.getenv('ECHO_AGENT_URL'))

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
# and regularly queries the the location service
# Returns the interval so you can stop it
# NOTE: It will make sure not to attach twice to the same car
picked_vehicle_ids = []
picked_vehicle_intervals = []
def start_driving(service_query_interval=5):
  # 0.) Connect to the client and retrieve the world object
  client = carla.Client(CARLA_URL, CARLA_PORT)
  world = client.get_world()

  # 1.) Wait for actors to become available (will raise an error if it fails)
  wait_for_actors(world)

  # 2.) Get a random car from the ones driving around 
  all_vehicles = world.get_actors().filter('*vehicle*')
  ego_vehicle = None
  if len(all_vehicles) == len(picked_vehicle_ids):
     # Cannot start more simulations, so just do nothing
     return len(picked_vehicle_ids)
  while ego_vehicle == None:
    ego_vehicle = random.choice(list(all_vehicles))
    if ego_vehicle.id in picked_vehicle_ids:
       ego_vehicle = None

  print('Picked a vehicle. Start tracking...')

  # 3.) Call service regularly with a random user id
  user_id = 'carla-' + str(random.choice(range(1, 100000)))

  def log_location():
      location = ego_vehicle.get_location()
      geo_location = world.get_map().transform_to_geolocation(location)
      requests.get(
         ECHO_AGENT_URL + '/anonymous_resource',
         params={
            'user_id': user_id,
            'x': geo_location.latitude,
            'y': geo_location.longitude,
            'service_name': 'service'
         }
      )
  
  picked_vehicle_intervals.append(set_interval(log_location, service_query_interval))
  picked_vehicle_ids.append(ego_vehicle.id)

  return len(picked_vehicle_intervals)

# Stops all simulated cars
# (cars in carla will continue to drive though,
# this just cancels the attachment to the cars)
# Returns the number of cars stopped
def stop_all():
  for interval in picked_vehicle_intervals:
    interval.cancel()
  number_of_intervals = len(picked_vehicle_intervals)
  picked_vehicle_intervals.clear()
  picked_vehicle_ids.clear()
  return number_of_intervals
