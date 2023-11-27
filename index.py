import carla
import random
import time
import threading

# Helpers

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
world = client.get_world()


##################################################
# First step: Get a real trajectory              #
##################################################

# 0.) Wait for actors to become available
retry_count = 10
while retry_count > 0:
    if len(world.get_actors()) > 0:
        break
    else:
        time.sleep(1.0)

if retry_count == 0 and len(world.get_actors()) == 0:
    raise ValueError('Actors not populated in time')

# 1.) Get a random car from the ones driving around 
all_vehicles = world.get_actors().filter('*vehicle*')
ego_vehicle = random.choice(list(all_vehicles))

print('Picked a vehicle. Start tracking...')

# 2.) Watch the car from the top
spectator = world.get_spectator()

def update_spectator_location():
    transform = ego_vehicle.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50),
    carla.Rotation(pitch=-90)))

set_interval(update_spectator_location, 1.0/24.0)

# 3.) Add a GPS sensor and log location
def log_location():
    location = ego_vehicle.get_location()
    print(location)

set_interval(log_location, 5)