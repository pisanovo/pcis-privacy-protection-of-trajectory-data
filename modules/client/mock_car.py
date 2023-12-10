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

# The main function of this script.
# It attaches to one of the simulated cars in Carla
# and regularly queries the the location service
def start_driving(service_query_interval, ):
  # 0.) Connect to the client and retrieve the world object
  client = carla.Client(CARLA_URL, CARLA_PORT)
  world = client.get_world()

  # 1.) Wait for actors to become available
  retry_count = 10
  while retry_count > 0:
      if len(world.get_actors()) > 0:
          break
      else:
          time.sleep(1.0)

  if retry_count == 0 and len(world.get_actors()) == 0:
      raise ValueError('Actors not populated in time')

  # 2.) Get a random car from the ones driving around 
  all_vehicles = world.get_actors().filter('*vehicle*')
  ego_vehicle = random.choice(list(all_vehicles))

  print('Picked a vehicle. Start tracking...')

  # 3.) Watch the car from the top
  spectator = world.get_spectator()

  def update_spectator_location():
      transform = ego_vehicle.get_transform()
      spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50),
      carla.Rotation(pitch=-90)))

  set_interval(update_spectator_location, 1.0/24.0)

  # 4.) Call service regularly
  def log_location():
      location = ego_vehicle.get_location()
      requests.get(ECHO_AGENT_URL + '/anonymous_resource', params={location: location})
  
  set_interval(log_location, 5)