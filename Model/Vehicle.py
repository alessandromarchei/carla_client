
#====================================
# ===    CARLA emulator client    ===
# ===   -----------------------   ===
# ===  Vehicle object definition  ===
#====================================

import os
import json

from Model.CarlaObject import CarlaObject
from dicttoxml import dicttoxml

from Model.Position import Position
from Model.VehicleMotionParams import VehicleMotionParameters
from Model.VideoCam import VideoCam

# https://medium.com/analytics-vidhya/spawning-vehicles-in-carla-86429f767040
class Vehicle(CarlaObject):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Vehicle nick name
    Name: None

    # Vehicle manufacturer
    Manufacturer: None

    # Vehicle model
    Model: None

    # Vehicle class
    Class: None

    # Vehicle generation
    Generation: None

    # Vehicle string identifier for Carla' Blueprint library
    BlueprintID: None

    # Vehicle base type
    BaseType: None

    # Vehicle special type
    SpecialType: None

    # Vehicle has lights flag
    HasLights: False

    # Vehicle has opening doors flag
    HasOpeningDoors: False
    
    # Installed video cams collection
    InstalledVideoCams: None

    # Vehicle motion parameters set
    MotionParameters: None

    # --- Vehicle position in CARLA's coordinate system
    currentPosition = None

    # --- Vehicle current status
    status = False

    # --- Ego vehicle sign
    isEgo = False

    #--------------------
    #--- Constructor  ---
    #--------------------

    # Id: vehicle identifier
    # Manufacturer: Vehicle manufacturer
    # Model: Vehicle model
    # Class: Vehicle class
    # Generation: Vehicle generation
    # BlueprintID: Vehicle string identifier for Carla' Blueprint library
    # BaseType: Vehicle base type
    # SpecialType: Vehicle special type
    # HasLights: Vehicle has lights flag
    # HasOpeningDoors: Vehicle has opening doors flag
    # InstalledVideoCams: installed video cams collection 
    # MotionParameters: current vehicle motion parameters
    # currentPosition: current vehicle position
    # status: Vehicle current status
    def __init__(self, Uuid = "", Name = "", Manufacturer = "", Model = "", 
                 Class = "", Generation = "", BlueprintID = "", 
                 BaseType = "", SpecialType = "", 
                 HasLights = False, HasOpeningDoors = False,
                 InstalledVideoCams = None, MotionParameters = None,
                 currentPosition = None, status = 0, isEgo = False):
        super().__init__(Uuid);
        self.Name = Name
        self.Manufacturer = Manufacturer
        self.Model = Model
        self.Class = Class
        self.Generation = Generation
        self.BlueprintID = BlueprintID
        self.BaseType = BaseType
        self.SpecialType = SpecialType
        self.HasLights = HasLights
        self.HasOpeningDoors = HasOpeningDoors
        if InstalledVideoCams is None:
            self.InstalledVideoCams = list()
        else:
            self.InstalledVideoCams = InstalledVideoCams

        self.MotionParameters = VehicleMotionParameters()
        self.currentPosition = Position(0, 0, 0, 0)
        self.status = status
        self.isEgo = False

    #--------------------

    #-----------------------
    #--- Public methods  ---
    #-----------------------
    
    # Deserialize Xml node into vehicle object
    # item: Xml node to be deserialized
    def deserialize(self, path):

        if (os.path.exists(path)):

            with open(path) as f:
                jsondata = f.read()
            
            decoded = Vehicle(**json.loads(jsondata))

            self.Uuid = decoded.Uuid
            self.Name = decoded.Name
            self.Manufacturer = decoded.Manufacturer
            self.Model = decoded.Model
            self.Class = decoded.Class
            self.Generation = decoded.Generation
            self.BlueprintID = decoded.BlueprintID
            self.BaseType = decoded.BaseType
            self.SpecialType = decoded.SpecialType
            self.HasLights = decoded.HasLights
            self.HasOpeningDoors = decoded.HasOpeningDoors
            self.isEgo = decoded.isEgo
    
            self.InstalledVideoCams = list()

            for vc in decoded.InstalledVideoCams:
                decodedVc = VideoCam(**vc)
                decodedVc.position = Position(**decodedVc.position)
                self.InstalledVideoCams.append(decodedVc)

            return True

    # --- Serialize object to xml file
    # --- path: path to saved files location
    # --- printXml: copy Xml to output window if true, otherwise false
    def serialize(self, path, printXml):

        jsondata = json.dumps(self.__dict__, 
            default=lambda o: o.__dict__, indent=4)
        
        if printXml == True:
            print(jsondata)

        # Write to Xml file
        with open("{}\\{}.json".format(path, self.Uuid), 'w') as f:
            f.write(jsondata);

    # --- Get current vehicle status text description
    def get_status_text(self):

        match self.status:
            case 0:
                return "Idle"
            case 1:
                return "Spawned"
            case 2:
                return "Auto-running"
            case 3:
                return "Ego (manual)"

        return "?"

