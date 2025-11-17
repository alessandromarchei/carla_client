
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===   Generic actor position definition   ===
#==============================================

class MovingParamsItem(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # --- Current sensor index 
    sensorIndex = 0

    # Vehicle current velocity (kmph)
    velocityKmph = 0;

    # Vehicle current velocity (mps)
    velocityMps = 0;

    # Vehicle velocity acceleration
    acceleration = 0;

    # Vehicle angle velocity
    angleVelocity = 0;

    # Vehicle wheels steering angle
    wheelsSteeringAngle = 0;

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # sensorIndex: current sensor index
    # velocityKmph: vehicle current velocity (kmph)
    # velocityMps: vehicle current velocity (mps)
    # acceleration: vehicle velocity acceleration
    # angleVelocity: vehicle angle velocity
    # wheelsSteeringAngle: vehicle wheels steering angle
    def __init__(self, sensorIndex, velocityKmph, velocityMps, 
                 acceleration, angleVelocity, wheelsSteeringAngle):
        self.sensorIndex = sensorIndex
        self.velocityKmph = velocityKmph
        self.velocityMps = velocityMps
        self.acceleration = acceleration
        self.angleVelocity = angleVelocity
        self.wheelsSteeringAngle = wheelsSteeringAngle

    #--------------------

