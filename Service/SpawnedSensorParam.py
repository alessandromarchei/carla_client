
#===========================================================
# ===               CARLA emulator client                ===
# ===   -----------------------------------------------  ===
# ===     Spawned sensor parameters object definition    ===
#===========================================================

class SpawnedSensorParamItem(object):

    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- Image width/height ratio
    imageRatio = 1

    # --- Parent sensor vehicle name
    parentVehicleName = ""

    # --- Own sensor name
    sensorName = ""

    # --- Sensor Uuid
    parentUuid = ""

    # --- Parent vehicle UUID
    parentVehicleUuid = ""

    # --- Video stream frame width
    imgWidth = 0

    # --- Video stream frame height
    imgHeight = 0

    ownSensor: None

    #-------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- imageRatio: image width/height ratio
    # --- parentVehicleName: parent sensor vehicle name
    # --- sensorName: own sensor name
    # --- width: video stream frame width
    # --- height: video stream frame height
    # --- parentUuid: sensor UUID
    # --- parentVehicleUuid: parent vehicle UUID
    def __init__(self, imageRatio, parentVehicleName, sensorName, parentUuid, 
                 width, height, parentVehicleUuid, ownSensor):

        self.imageRatio = imageRatio
        self.parentVehicleName = parentVehicleName
        self.sensorName = sensorName
        self.parentUuid = parentUuid
        self.imgWidth = width
        self.imgHeight = height
        self.parentVehicleUuid = parentVehicleUuid
        self.ownSensor = ownSensor

    #--------------------

