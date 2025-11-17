
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===  Vehicle control package definition   ===
#==============================================

class ControlDataPackageItem(object):

    # -----------------    
    # --- Constants ---
    # -----------------

    # --- Received parameters max bound
    maxBound = 32767

    # --- Maximum steering wheel angle
    maxSteeringWheelAngle = 450.0

    # -------------------------    
    # --- Public properties ---
    # -------------------------

    # --- Required wheel position
    wheelPosition = 0

    # --- Required wheel angle
    wheelAngle = 0

    # --- Required accelerator position
    acceleratorPosition = 0

    # --- Required brake position
    brakePosition = 0

    # --- Required clutch position
    clutchPosition = 0

    # --- Required gear position
    gearPosition = 0

    # --- Required button Id state
    buttonIdIsPressed = 0

    # --- Default contructor
    # dataArray: received control unit data array
    def __init__(self, dataArray):

        if dataArray is not None:
            self.wheelPosition = dataArray[0]  
            self.wheelAngle = dataArray[1] / self.maxSteeringWheelAngle
            self.acceleratorPosition = dataArray[2]
            self.brakePosition = dataArray[3] 
            self.clutchPosition = dataArray[4]
            self.gearPosition = dataArray[5]
            self.buttonIdIsPressed = dataArray[6]
            print("WP: {}, WA: {}, AP: {}, BP: {}, CP: {}, GP: {}, BP: {}".format(
                self.wheelPosition, self.wheelAngle,
                self.acceleratorPosition, self.brakePosition,
                self.clutchPosition, self.gearPosition, self.buttonIdIsPressed))
