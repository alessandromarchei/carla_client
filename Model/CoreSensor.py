
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===       Generic sensor definition       ===
#==============================================

from dicttoxml import dicttoxml
import xml.dom.minidom
from lxml import etree, objectify

from Model.CarlaObject import CarlaObject
from Model.Position import Position

class SensorCore(CarlaObject):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Sensor name
    name = "Generic sensor";

    # Sensor position object
    position = None

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # uuid: object identifier
    # name: sensor name
    # position: Sensor position object
    def __init__(self, uuid, name, position=None):
        super().__init__(uuid);
        self.name = name;
        self.position = position

    #--------------------

    #-----------------------
    #--- Public methods  ---
    #-----------------------

    # --- Deserialize object from xml file
    # --- filename: Xml file to be processed name
    def deserialize(self, filename):

        try:
            # Read Xml file by its filename
            with open(filename) as f:
                xml = f.read()
        
            # Decode Xml structure
            res = objectify.fromstring(xml)

            # Loop through Xml nodes and fill Self properties
            for item in res.getchildren():
                match item.tag:
                    case 'vehicleId':
                        self.vehicleId = item
                    case 'name':
                        self.name = item
            return res

        except Exception as e:
            print("Exception is occured (Wrong Xml file?): {}".format(str(e)))
            return None

    # --------------------------------------------------
