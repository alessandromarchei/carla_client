
#====================================================
# ===            CARLA emulator client            ===
# ===   ---------------------------------------   ===
# ===   Vehicle collision definition definition   ===
#====================================================

class CollisionDefinition(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # --- Allow automatic lane changes for spawned vehicle
    autoLaneChange = False;

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # autoLaneChange: Allow automatic lane changes for spawned vehicle
    def __init__(self, autoLaneChange = False):

        self.autoLaneChange = autoLaneChange;

    #--------------------

