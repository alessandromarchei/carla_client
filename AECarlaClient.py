from ast import Lambda
from Gui.MainWindow import MainWindow
from Service.CarlaProcessor import CarlaProcessorService
from Service.Settings import Settings_Set
from Service.VehiclesProcessor import VehiclesProcessor
import carla
import random
import datetime
import time
import io

#=================================================================

# https://pythonprogramming.net/reinforcement-learning-self-driving-autonomous-cars-carla-python/


vp = VehiclesProcessor()

carlaConnector = CarlaProcessorService()

#vp.save(".", availableVehicles)

usedVehicles = vp.loadusedvehicles(".")

settings = Settings_Set("./settings.json")

settings.deserialize()

# === Tkinter GUI

mainWnd = MainWindow("CARLA client 0.10", carlaConnector,
                     usedVehicles, settings)







