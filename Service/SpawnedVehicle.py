
#================================================
# ===          CARLA emulator client          ===
# ===   ------------------------------------  ===
# ===     Full spawned vehicle description    ===
#================================================

class SpawnedVehicleItem:

    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- CARLA system spawned vehicle object
    carlaVehicleObj: None

    # --- CARLA system basic blueprint vehicle object
    carlaBlueprintObj: None

    # --- Client vehicle object
    ownVehicleObj: None

    # --- Vehicle common behavior profile name
    behaviorName: None

    # --- Vehicle will ignore traffic lights flag
    ignore_traffic_lights = False

    # --- Vehicle will ignore stop signs flag
    ignore_stop_signs = False

    # --- Vehicle will ignore other vehicles flag
    ignore_vehicles = False

    #-------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- carlaVehicleObj: CARLA system spawned vehicle object
    # --- ownVehicleObj: client vehicle object
    # --- behaviorName: vehicle behaviour profile name
    # --- ignoreTrafficLights: Vehicle will ignore traffic lights flag
    # --- ignoreStopSigns: Vehicle will ignore stop signs flag
    # --- ignoreVehicles: Vehicle will ignore other vehicles flag
    def __init__(self, carlaVehicleObj, ownVehicleObj, blueprintObj, 
                 behaviorName,
                 ignoreTrafficLights,
                 ignoreStopSigns,
                 ignoreVehicles):

        self.carlaVehicleObj = carlaVehicleObj
        self.carlaBlueprintObj = blueprintObj
        self.ownVehicleObj = ownVehicleObj
        self.behaviorName = behaviorName
        self.ignore_traffic_lights = ignoreTrafficLights
        self.ignore_stop_signs = ignoreStopSigns
        self.ignore_vehicles = ignoreVehicles

    #--------------------




