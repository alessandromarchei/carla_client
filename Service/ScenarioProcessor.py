
import math
import random
import carla

from Model.TrafficScenarioVehicle import TrafficScenarioVehicleItem 

# --------------------------------------------------
# --- Traffic scenarios processor implementation ---
# --------------------------------------------------
class TrafficScenarioProcessor(object):

    # --- Public properties

    carla = None

    trafficVehicles = None

    # --- CARLA world object reference
    carlaWorld = None

    # --- Default constructor 
    def __init__(self, carlaWorld):
        print("Initialize traffic scenarion processor")
        self.carlaWorld = carlaWorld

    # --- Create particular traffic scenario vehicle
    # kind: vehicle kind which defines how to place 
    # baseVehicle: relative base vehicle to place new one
    # allVehicles: all installed Carla vehicles collection
    # azimuth: azimuth from base position to place vehicle (degrees)
    # distance: distance from base position to place vehicle (meters) 
    def createTrafficVehicle(self, kind, baseVehicle, allVehicles, 
        azimuth = None, distance = None):
        
        print("Create traffic scenario vehicle: {}".format(kind))
        
        match kind:
            case "Leader":
                print("Leader")
            case "Follover":    
                print("Follover")

        newVehicle = random.choice(allVehicles)

        spawn_point = TrafficScenarioProcessor.GetVehiclePosition(
            baseVehicle, azimuth, distance)

        if newVehicle.has_attribute('color'):
            color = random.choice(newVehicle.get_attribute('color').recommended_values)
            newVehicle.set_attribute('color', color)

        newVehicleObj = self.carlaWorld.spawn_actor(
            newVehicle, spawn_point)

    # --- 
    def processTrafficVehicleMoving():
        print("Moving step")

    # --- Get spawn point before specified vehicle inside specified radius  
    # --- vehicle: vehicle to be processed
    # --- distance: distance from vehicle to spawn obstacle (meters) 
    # --- angle: direction from vehicle to spawn obstacle (degrees)
    @staticmethod
    def GetVehiclePosition(vehicle, distance, angle):
        
        transform = vehicle.get_transform()

        radians_rotation = transform.rotation.yaw * math.pi / 180  # Convert yaw to radians
        radians_angle = angle * math.pi / 180

        spawn_x = transform.location.x + math.cos(radians_rotation + radians_angle) * distance
        spawn_y = transform.location.y + math.sin(radians_rotation + radians_angle) * distance
        spawn_z = transform.location.z  # Keep the same Z coordinate
    
        new_spawn_point = carla.Transform(
            carla.Location(x=spawn_x, y=spawn_y, z=spawn_z),
                transform.rotation)  # Match the ego vehicle's rotation or adjust as needed

        return new_spawn_point



