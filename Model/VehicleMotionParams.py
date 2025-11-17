
#=================================================
# ===           CARLA emulator client          ===
# ===   ------------------------------------   ===
# ===   Vehicle motion parameters definition   ===
#=================================================

class VehicleMotionParameters(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Current throttling level
    throttling: 0

    # Current breaking level
    breaking: 0

    #--------------------
    #--- Constructor  ---
    #--------------------

    def __init__(self):
        self.throttling = 0
        self.breaking = 0



