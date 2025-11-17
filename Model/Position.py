
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===   Generic actor position definition   ===
#==============================================

class Position(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Actor position at X-axis
    positionX = 1.6;

    # Actor position at Y-axis
    positionY = 0;

    # Actor position at Z-axis
    positionZ = 1.7;

    # Actor rotation
    rotation = 0;

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # positionX: Actor position at X-axis
    # positionY: Actor position at Y-axis
    # positionZ: Actor position at Z-axis
    # rotation: Actor rotation
    def __init__(self, positionX, positionY, positionZ, rotation):
        self.positionX = positionX;
        self.positionY = positionY;
        self.positionZ = positionZ;
        self.rotation = rotation

    #--------------------

