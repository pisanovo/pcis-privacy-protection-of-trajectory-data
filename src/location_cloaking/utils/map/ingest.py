import carla
import xml.etree.ElementTree as ET
from location_cloaking.config import CarlaConfig

"""
Script which can be used to load open_drive map files into Carla

Usage: 
- Specify your open_drive map file by changing MAP_PATH and run

Note:
- See osm_to_xodr.py for instructions on how to obtain a valid open drive file for Carla
"""

MAP_PATH = "/code/src/location_cloaking/utils/map/map_files/map_uni_stuttgart_and_vaihingen.xodr"

client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
# Long timeout since loading map may take some time, where carla remains unresponsive
client.set_timeout(100000)

myFile = ET.parse(MAP_PATH)
root = myFile.getroot()
xodr_str = ET.tostring(root, encoding="utf8", method="xml")

vertex_distance = 2.0        # in meters
max_road_length = 50.0       # in meters
# Not recommended to specify >0 wall height to prevent vehicles from falling of as it will result in vehicles getting
# stuck
wall_height = 0.0            # in meters

# In case vehicles are falling off the map use very large extra width for junctions (otherwise set to 0)
# TODO: Find a better solution
junction_extra_width = 750                              # in meters

world = client.generate_opendrive_world(
    xodr_str, carla.OpendriveGenerationParameters(
        vertex_distance=vertex_distance,
        max_road_length=max_road_length,
        wall_height=wall_height,
        additional_width=junction_extra_width,
        smooth_junctions=True,
        enable_mesh_visibility=True,
        enable_pedestrian_navigation=False
))
