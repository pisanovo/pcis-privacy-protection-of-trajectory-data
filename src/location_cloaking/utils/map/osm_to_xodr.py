import carla

# Read the .osm data
f = open("/home/vincenzo/PycharmProjects/DataIntensiveComputing/src/location_cloaking/utils/map/map_files/map_uni_l.osm", 'r')
osm_data = f.read()
f.close()

# Define the desired settings. In this case, default values.
settings = carla.Osm2OdrSettings()
# Set OSM road types to export to OpenDRIVE
settings.set_osm_way_types(["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link", "unclassified", "residential"])
# Convert to .xodr
settings.center_map = False
settings.use_offsets = False
# Change this according to your map
settings.proj_string = "+proj=tmerc +lat_0=48.7525 +lon_0=9.0879"
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open("/home/vincenzo/PycharmProjects/DataIntensiveComputing/src/location_cloaking/utils/map/map_files/map_uni_l_test.xodr", 'w')
f.write(xodr_data)
f.close()