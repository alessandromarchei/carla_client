
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===   Generic actor position definition   ===
#==============================================

class ControlledVehicleItem(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Parent vehicle UUID
    parentUuid = "";

    # Controlled vehicle object (BehaviorAgent)
    controlledVehicle = None

    # Moving vehicle flag
    isMoving = False

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # parentUuid: Parent vehicle UUID
    # controlledVehicle: Controlled vehicle object (BehaviorAgent)
    # isMoving: moving vehicle flag
    def __init__(self, parentUuid, controlledVehicle, isMoving):
        self.parentUuid = parentUuid;
        self.controlledVehicle = controlledVehicle;
        self.isMoving = isMoving

    #--------------------

