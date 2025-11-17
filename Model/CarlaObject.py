
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===       Generic object definition       ===
#==============================================

class CarlaObject(object):

    # Vehicle internal identifier
    Uuid: None

    #--------------------
    #--- Constructor  ---
    #--------------------

    # Id: vehicle identifier
    def __init__(self, Uuid):
        self.Uuid = Uuid

    #--------------------


