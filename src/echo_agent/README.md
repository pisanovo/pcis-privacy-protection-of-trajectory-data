# Echo agent algorithm

TODO: Add a section about the algorithm itself

## Setup

0. Add two secrets files `./secrets/db_password.txt` and `./secrets/db_root_password.txt`. They should contain the passwords for the db and are ignored by git.
1. Install docker and docker compose.
2. Visit the docker compose.yaml and fill out the environment variables pointing to your carla installation (CARLA_URL and CARLA_PORT)
3. Run `docker compose up --build` to start the system. 
4. Run health check: `curl http://localhost:5000/health`. If status is not okay, the database likely started up to slow. Wait a minute and restart the echo_agent `docker compose stop echo_agent`, then `docker compose start echo_agent`.
5. Make sure at least one car is driving on the carla instance, e.g. by running the script setup.py. To do that from a container, run `docker run --rm -v ./:/code --network="host" -it python:3.7-bookworm bash`. Then in the container, cd into the code `cd /code`, upgrade pip `pip install --upgrade pip` and install the modules `pip3 install -r requirements.txt`. Then, you can run the setup (or do whatever else you like to do).

You're done! The modules from the `./modules` folder are now mounted into the respective service containers.

## Use

Call the `/start` route to start the simulation.
