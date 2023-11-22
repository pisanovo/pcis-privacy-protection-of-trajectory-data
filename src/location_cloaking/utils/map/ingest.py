import carla
import xml.etree.ElementTree as ET
from location_cloaking.config import CarlaConfig

client = carla.Client(CarlaConfig.HOST, CarlaConfig.PORT)
# Long timeout since loading map may take some time, where carla remains unresponsive
client.set_timeout(100000)

myFile = ET.parse("../map/map_files/map_uni_stuttgart_and_vaihingen.xodr")
root = myFile.getroot()
xodr_str = ET.tostring(root, encoding="utf8", method="xml")

vertex_distance = 2.0                                   # in meters
max_road_length = 50.0                                  # in meters
wall_height = 0.0                                       # in meters
# In case vehicles are falling off the map use very large extra width for junctions (otherwise set to 0)
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
