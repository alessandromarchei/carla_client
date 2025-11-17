
#====================================
# ===    CARLA emulator client    ===
# ===   -----------------------   ===
# === Video cam sensor definition ===
#====================================

from Model.CoreSensor import SensorCore
from dicttoxml import dicttoxml
from lxml import etree, objectify
from Model.Position import Position

class VideoCam(SensorCore):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Frame size at X-axis (pixels)
    frameSizeX = 640.0;

    # Frame size at Y-axis (pixels)
    frameSizeY = 480.0;

    # Field of vision (degrees)
    fieldOfVision = 90.0;

    # Rotation around pitch axis
    rotationPitch = 0.0;

    # Rotation around yaw axis
    rotationYaw = 0.0;

    # Rotation around roll axis
    rotationRoll = 0.0;

    # Kind of post processing
    postProcessing = "Depth";

    # --- Time in seconds between sensor captures
    frameRate = 1.0

    # --- Is this sensor front one flag
    isFront = False

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # name: sensor name
    # pX: Sensor position at X-axis
    # pY: Sensor position at Y-axis
    # pZ: Sensor position at Z-axis
    # frameSizeX: Frame size at X-axis (pixels)
    # frameSizeY: Frame size at Y-axis (pixels)
    # fov: Field of vision (degrees)
    # rotationPitch: Rotation around pitch axis
    # rotationYaw: Rotation around yaw axis
    # rotationRoll: Rotation around roll axis
    # postProcessing: Post processing kind
    # frameRate: Time in seconds between sensor captures
    # isFront: Is this sensor front one flag
    def __init__(self, Uuid = "", name = "Generic sensor", 
                frameSizeX = 640, frameSizeY = 480,
                fieldOfVision = 90.0, rotationPitch = 0, rotationYaw = 0, rotationRoll = 0,
                postProcessing = "Depth", frameRate = 0.5, position = Position(1.6, 0, 1.7, 0),
                isFront = False):
        super().__init__(Uuid, name, position);
        self.frameSizeX = frameSizeX;
        self.frameSizeY = frameSizeY;
        self.fieldOfVision = fieldOfVision;
        self.rotationPitch = rotationPitch;
        self.rotationYaw = rotationYaw;
        self.rotationRoll = rotationRoll;
        self.postProcessing = postProcessing;
        self.frameRate = frameRate
        self.isFront = isFront

    #--------------------

    #-----------------------
    #--- Public methods  ---
    #-----------------------

    # --- Deserialize object from xml file
    # --- filename: Xml file to be processed name
    def deserialize(self, filename):

        try:
            
            # Read Xml and deserialize base class properties        
            xml = super().deserialize(filename)

            if xml is not None:

                # Loop through Xml nodes and fill Self properties
                for item in xml.getchildren():

                    match item.tag:
                        case 'frameSizeX':
                            self.frameSizeX = int(item)
                        case 'frameSizeY':
                            self.frameSizeY = int(item)
                        case 'fieldOfVision':
                            self.fieldOfVision = float(item)
                        case 'rotationPitch':
                            self.rotationPitch = float(item)
                        case 'rotationYaw':
                            self.rotationYaw = float(item)
                        case 'rotationRoll':
                            self.rotationRoll = float(item)
                        case 'postProcessing':
                            self.postProcessing = item
                        case 'frameRate':
                            self.frameRate = float(item)
                        case 'isFront':
                            self.isFront = bool(item)
        
                print("Deserialized object:")
                self.display()

                return True

        except Exception as e:
            print("Exception: {}".format(str(e)))
            return False

    #--------------------

    # Display object properties in output window
    def display(self):
        print("Name={0}, X={1:.2f}, Y={2:.2f}, Z={3:.2f}, FrameX={4:.0f}, FrameY={5:.0f}, "
              "FOV={6:.2f}, Pitch={7:.2f}, Yaw={8:.2f}, Roll={9:.2f}, "
              "Post processing: {10}, Rate = {11:.2f}, Is front: {}"
              .format(self.name, self.positionX, self.positionY, self.positionZ, self.frameSizeX, self.frameSizeY,
                self.fieldOfVision, self.rotationPitch, self.rotationYaw, self.rotationRoll,
                self.postProcessing, self.frameRate, self.isFront))

    #--------------------
