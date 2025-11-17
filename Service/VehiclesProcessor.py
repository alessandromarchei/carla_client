
#==========================================
# ===       CARLA emulator client       ===
# ===   -----------------------------   ===
# === Vehicles serialization processor  ===
#==========================================

import uuid
import os
import os.path
from Model.VideoCam import VideoCam
from Model.Vehicle import Vehicle

class VehiclesProcessor(object):

    #--------------------
    #--- Constructor  ---
    #--------------------

    # Id: vehicle identifier
    def __init__(self):
        pass

    #--------------------

    #----------------------
    #--- Public methods
    #----------------------

    #--- Load used vehicles from json files
    #--- Path to the Json files location
    def loadusedvehicles(self, path):

        res = list()

        # Get all items in the specified directory
        items = os.listdir(path)

        # Loop through retrieved items
        for item in items:

            # If item is file
            if os.path.isfile(os.path.join(path, item)):

                # If item is Xml file
                if(os.path.splitext(item)[1] == ".json"):
        
                    print("Processing file:")
                    print(os.path.join(path, item))

                    # Attempt to deserialize Json file
                    vehicle = Vehicle()

                    try:
                        if vehicle.deserialize(os.path.join(path, item)) == True:
                            res.append(vehicle)
                    except Exception as ex:
                        print("Wrong file format: {}".format(ex))

        return res

    #--- Load all available vehicles from CARLA API
    def loadavailablevehicles(self):

        res = list()

        res.append(Vehicle(str(uuid.uuid4()), "Street 1 car", "Dodge", "Charger 2020", "Standard",
                   2, "vehicle.dodge.charger_2020", "car", "None", True, True))
        res.append(Vehicle(str(uuid.uuid4()), "Street 2 car", "Dodge", "Police Charger", "Standard",
                   1, "vehicle.dodge.charger_police", "car", "emergency", False, False))
        res.append(Vehicle(str(uuid.uuid4()), "Street 3 car", "Dodge", "Police Charger 2020", "Standard",
                   2, "vehicle.dodge.charger_police_2020", "car", "emergency",True, True))
        res.append(Vehicle(str(uuid.uuid4()), "Street 4 car", "Ford", "Crown (taxi)", "Standard",
                   2, "vehicle.ford.crown", "car", "taxi", True, True))
        res.append(Vehicle(str(uuid.uuid4()), "Street 5 car", "Ford", "Mustang", "Standard",
                   1, "vehicle.ford.mustang", "car", "None", False, False))
        res.append(Vehicle(str(uuid.uuid4()), "Street 6 car", "Jeep", "Wrangler Rubicon", "Compact",
                   1, "vehicle.jeep.wrangler_rubicon", "car", "None", False, False))
        res.append(Vehicle(str(uuid.uuid4()), "Street 7 car", "Lincoln", "MKZ 2017", "Standard",
                   1, "vehicle.lincoln.mkz_2017", "car", "None", False, False))

        for item in res:
            for i in range(1, 4):
                vc = VideoCam(str(uuid.uuid4()),
                    "Sensor XYZ-{}".format(item.Model), 14, 21,
                    44, 1028, 744,
                    180.0, 0, 0, 0, "Depth map-{}".format(i))
                #item.InstalledVideoCams.append(vc)

        return res


    #------------------------------
    #--- Debug purposes methods
    #------------------------------

    #--- Save vehicles collection as set of JSON files
    #--- vehicles: Vehicles collection to be saved
    def save(self, path, vehicles):

        for item in vehicles:
            item.serialize(".", True)
