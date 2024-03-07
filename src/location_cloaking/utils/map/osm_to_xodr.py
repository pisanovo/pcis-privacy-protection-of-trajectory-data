import carla

"""
Script convert openstreetmap maps to open_drive for Carla

!!! Note this script only serves a sub step, see the following instructions for full details !!!
Due to various Carla bugs creating a valid map involves multiple steps

Instructions:
1. With openstreetmap select the export option and note down the minimum latitude and longitude of your selection area
   then save the map file
2. Convert the openstreetmap to open_drive using this script, don't forget to set MIN_LATITUDE and MIN_LONGITUDE
3. Download SUMO, e.g., at https://sumo.dlr.de/docs/Downloads.php
4. Using SUMO netconvert (https://sumo.dlr.de/docs/netconvert.html), convert the openstreetmap to open_drive following
   the example prompt
   
   Example prompt:
   netconvert 
   --osm-files map_uni_l.osm 
   --opendrive-output map_uni_l.xodr 
   --proj "+proj=tmerc +lat_0=48.7525 +lon_0=9.0879" 
   --remove-edges.by-vclass rail_slow,rail_fast,bicycle,pedestrian,hov,taxi,bus,delivery,transport,lightrail,cityrail,motorcycle,rail,truck,tram,rail_urban 
   --offset.disable-normalization true 
   --default.spreadtype roadCenter 
   --no-turnarounds.except-deadend true
   
   Notes:
   - Very important to specify the proj which is again your MIN_LATITUDE and MIN_LONGITUDE, and set 
   --offset.disable-normalization to true (leave +proj=tmerc as is)
   - Removing certain class edges makes sure that the resulting map boundaries are close enough
   - This _should_ also work without --default.spreadtype and --no-turnarounds.except-deadend
   
5. Open the generated open_drive map in step 4. and copy from the OPENDRIVE header the north, south, east and west bounds

   Example:
       <OpenDRIVE>
        <header revMajor="1" revMinor="4" name="" version="1.00" date="Tue Nov 21 11:49:46 2023" north="1495.23" south="-3493.67" east="4061.31" west="-822.82">
            <geoReference>
       <![CDATA[
         +proj=tmerc +lat_0=48.7525 +lon_0=9.0879
       ]]>
            </geoReference>
       </header>
       
       Result: 
       north="1495.23" south="-3493.67" east="4061.31" west="-822.82"
       
6. Copy the result from step 5 and replace it with the north, south, east and west bounds in the open_drive generated
   in step 3
7. Load the modified map from step 3+6 into Carla with ingest.py
"""

OSM_MAP_PATH = "../map/map_files/map_uni_l.osm"
XODR_MAP_PATH = "../map/map_files/map_uni_l_test.xodr"

MIN_LATITUDE = 48.7525
MIN_LONGITUDE = 9.0879


# Read the .osm data
f = open(OSM_MAP_PATH, 'r')
osm_data = f.read()
f.close()

settings = carla.Osm2OdrSettings()
# Set OSM road types to export to OpenDRIVE
settings.set_osm_way_types([
    "motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link",
    "tertiary", "tertiary_link", "unclassified", "residential"
])
# Convert to .xodr
settings.center_map = False
settings.use_offsets = False
settings.proj_string = f"+proj=tmerc +lat_0={MIN_LATITUDE} +lon_0={MIN_LONGITUDE}"
xodr_data = carla.Osm2Odr.convert(osm_data, settings)

# save opendrive file
f = open(XODR_MAP_PATH, 'w')
f.write(xodr_data)
f.close()