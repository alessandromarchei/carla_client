
#================================================
# ===          CARLA emulator client          ===
# ===   ------------------------------------  ===
# ===  CARLA simulator actions implementation ===
#================================================

import math
import carla
import threading
import time
import random
import asyncio
import io
import sys

from numpy import append
from queue import Queue

from Model.ControlledVehicle import ControlledVehicleItem
from Model.MovingParams import MovingParamsItem
from Service import ScenarioProcessor, SpawnedSensor
from Service.Enumerations import CarlaActor
from Service.PredictionServerConnector import PredictionUnitConnector
from Service.ScenarioProcessor import TrafficScenarioProcessor
from Service.SpawnedSensor import SpawnedSensorItem
from Service.SpawnedSensorParam import SpawnedSensorParamItem
from Service.SpawnedVehicle import SpawnedVehicleItem
from Model.ControlDataPackage import ControlDataPackageItem

# To import a behavior agent
from Service.VehicleControlConnector import VehicleControlUnitConnector
from agents.navigation.behavior_agent import BehaviorAgent

# --- https://roboticsknowledgebase.com/wiki/simulation/Spawning-and-Controlling-Vehicles-in-CARLA/
# --- https://carla.readthedocs.io/en/0.9.2/cameras_and_sensors/
# --- https://carla.readthedocs.io/en/latest/tuto_G_retrieve_data/#rgb-camera
# --- Ego vehicle: https://carla.readthedocs.io/en/0.9.15/adv_traffic_manager/#hybrid-physics-mode
# --- https://carla.readthedocs.io/en/latest/adv_agents/

# --- ROS image: https://github.com/carla-simulator/ros-bridge/blob/master/carla_ros_bridge/src/carla_ros_bridge/camera.py
# --- ROS Windows: https://docs.ros.org/en/kilted/Installation/Windows-Install-Binary.html#system-requirements

# --- https://github.com/carla-simulator/carla/issues/3876
# --- https://www.google.com/search?q=define+angle+between+2+points+by+coordinates&oq=define+angle+between+2+points+by+coo&gs_lcrp=EgZjaHJvbWUqCQgBECEYChigATIGCAAQRRg5MgkIARAhGAoYoAEyBwgCECEYjwIyBwgDECEYjwIyBwgEECEYjwLSAQkyMDk0OGowajSoAgCwAgE&sourceid=chrome&ie=UTF-8

# --- https://github.com/carla-simulator/carla/issues/1268

# --- https://github.com/carla-simulator/carla/issues/4743

class CarlaProcessorService_headless(object):

    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- Application settings reference
    app_settings = None
    
    # --- CARLA simulator syncronization thread existence flag
    stopSyncThreadRequest = False

    # --- Main Carla client object reference
    carlaClient = None

    # --- Currently active CARLA world (city map)
    carlaWorld = None

    # --- All available CARLA worlds (city maps) collection
    carlaMaps = None

    # --- Currently active world (city map) name
    carlaMap = None

    # --- Currently active world built-in vehicles collection
    carlaVehicles = None

    # --- Loaded blue-print library
    carlaBlueprintLibrary = None

    # --- Carla' traffic manager object reference
    carlaTrafficManager = None

    # --- Currently active video sensor
    activeVideoSensor = None

    # --- Active (spawned) video cams collection
    activeSensors = []

    # --- Spawned vehicles full descriptions collection
    spawned_vehicles = []

    # --- Currently selected spawned vehicle object
    selected_spawned_vehicle = None

    # --- Currently selected controlled vehicle object
    selected_controlled_vehicle = None

    # --- Activated traffic objects collection
    traffic_objects_list = []

    # --- Parent progress window reference
    progressWnd = None

    # --- All generated pedestrians collection
    walkers_list = []

    # --- All generated pedestrians and their controllers collection
    all_id = []

    # --- Successfully generated vehicles count
    spawned_generated_vehicles = 0

    # --- Error of generated vehicles count
    spawned_non_generated_vehicles = 0

    # --- Successfully generated walkers count
    spawned_generated_walkers = 0

    # --- Error of generated walkers count
    spawned_non_generated_walkers = 0

    # --- All world spawn points collection
    world_spawn_points = []

    # --- Vehicles are moving under autopilot collection
    vehicles_under_autopilot = []

    # --- Objects which have been generated as obstacles collection
    generated_obstacle_objects = []

    # --- Vehicle control unit connector object
    vcu_Connector = None

    # --- Prediction unit connector object
    tpu_Connector = None

    # --- Traffic scenario service object
    trafficScenarioProcessor = None

    # --- Generated pedestrians collection
    generated_pedestrians = []

    # --- Top-down view sensor object
    topDownSensor = None

    #-----------------------------------
    #--- Public properties (threads) ---
    #-----------------------------------

    # --- Connection to remote Carla server thread object
    carlaConnectionThread = None

    # --- Load CARLA world thread object
    carlaLoadWorldThread = None

    # --- Spawning CARLA actor thread object
    carlaSpawningActorThread = None

    # --- Start vehicle with auto-pilot thread
    carlaStartVehicleThread = None

    # --- Carla ticks issuer thread (for synchronuos mode)
    carlaSyncThread = None

    #-------------------------------------------
    #--- Public properties (events handlers) ---
    #-------------------------------------------

    # --- Connection to CARLA server attempt is completed event handler
    onConnectionAttemptCompleted = None

    # --- Load world and blueprint library attempt is completed event handler
    onLoadWorldAttemptCompleted = None

    # --- CARLA actor spawning attempt is completed event handler
    onActorHasBeenSpawned = None

    # --- Currently active video cam has recieved new frame event handler
    onNewVideoFrameIsRecieved = None

    # --- Vehicle control unit message is received event handler
    OnVehicleControlMessageReceived = None

    # --- Vehicle has been started in autopilot mode event handler
    onVehicleHasBeenStarted = None

    # --- Vehicle control unit is connected event handler
    onControlUnitConnectionAttemptCompleted = None

    # --- Prediction unit is connected event handler
    onPredictionUnitConnectionAttemptCompleted = None

    # --- Prediction server is replied event handler
    onPredictionUnitReplyReceived = None

    # --- CARLA' tick is done event handler
    onMovingStep = None

    # --- On top-down image recieved event handler
    OnTopDownImageReceived = None

    # --- For sync mode - process frame is done flag
    ProcessingIsDone = False

    #--------------------------------
    #--- Public methods (threads) ---
    #--------------------------------

    # --- Prepare and run Carla server connection thread
    # --- carlaUrl: CARLA server to be connected URL
    # --- carlaPort: CARLA server to be connected port
    # --- carlaTimeout: CARLA server to be connected connection timeout
    # --- carlaTMPort: CARLA server traffic manager port
    # --- carlaMode: CARLA simulator general mode
    # --- carlaDesiredFps: Requested fixed delay (for fixed timestamp modes)
    def RunCarlaConnectionThread(self, settings):

        self.app_settings = settings

        self.carlaConnectionThread = threading.Thread(target=self.carlaConnectionThreadExecutor, 
                                                     daemon=True)

        self.carlaConnectionThread.start()

        return self.carlaConnectionThread

    # --- Prepare and run load world (city) thread
    # --- carlaMap: map (city) to be loaded name
    def RunLoadCarlaWorldThread(self, settings, carlaMap):

        self.app_settings = settings

        self.carlaLoadWorldThread = threading.Thread(target=self.carlaLoadWorldThreadExecutor, 
                                                     daemon=True)

        self.carlaMap = carlaMap

        self.carlaLoadWorldThread.start()

        return self.carlaLoadWorldThread

    # --- Prepare and run Carla server spawning actor thread
    # --- actor: CARLA actor to be spawned
    # --- actorKind: CARLA actor to be spawned kind
    # --- behaviorName: vehicle behaviour profile name
    # --- progressWnd: parent progress window reference
    # --- ignoreTrafficLights: Vehicle will ignore traffic lights flag
    # --- ignoreStopSigns: Vehicle will ignore stop signs flag
    # --- ignoreVehicles: Vehicle will ignore other vehicles flag
    def RunSpawnActorThread(self, actor, actorKind, behaviorName, 
                 progressWnd,
                 ignoreTrafficLights,
                 ignoreStopSigns,
                 ignoreVehicles):

        self.progressWnd = progressWnd

        self.carlaSpawningActorThread = threading.Thread(target=self.carlaSpawningActorThreadExecutor, 
                                                     daemon=True,
                                                     args=(actor, actorKind, behaviorName,
                                                           None, None, None,
                                                           ignoreTrafficLights,
                                                           ignoreStopSigns,
                                                           ignoreVehicles))
        
        self.carlaSpawningActorThread.start()
        
        return self.carlaSpawningActorThread

    # --- Run vehicle in autopilot mode 
    def RunStartVehicleThread(self):

        self.carlaStartVehicleThread = threading.Thread(target=self.carlaStartVehicleThreadExecutor, 
                                                     daemon=True)
        
        self.carlaStartVehicleThread.start()
        return self.carlaStartVehicleThread

    stopped_index = -1

    # --- Stop selected vehicle auto-running mode
    def StopAutoRunning(self):

        index = 0

        for vehicle in self.vehicles_under_autopilot:
            if vehicle.controlledVehicle._vehicle.id == self.selected_spawned_vehicle.carlaVehicleObj.id:
                self.stopped_index = index
                return
            index = index + 1

    #------------------------------------------
    #--- Public methods (threads executors) ---
    #------------------------------------------

    # --- Carla server connection thread executor
    def carlaConnectionThreadExecutor(self):
    
        result = True
        error = ""

        try:
            
            print("[carla processor] Connecting to Carla server at {}:{}".format(
                self.app_settings.carlaServerUrl,
                self.app_settings.carlaServerMainPort))
            
            self.carlaClient = carla.Client(
                self.app_settings.carlaServerUrl, self.app_settings.carlaServerMainPort) 
            self.carlaClient.set_timeout(60000.0)

            # --- Convert .xodr into Carla world ---

            #carlaClient = carla.Client("192.168.1.139", 2000) 

            self.carlaWorld = self.carlaClient.get_world()
            
            # --- Get CARLA build-in maps (worlds) collection
            self.carlaMaps = self.carlaClient.get_available_maps()

        except Exception as e:

            error = str(e)
            print(error)
            result = False

        if self.onConnectionAttemptCompleted is not None:

            self.onConnectionAttemptCompleted(result, self.carlaMaps, error)

    # --- CARLA load world (city map) thread executor 
    def carlaLoadWorldThreadExecutor(self):

        result = True
        error = ""
        description = ""

        try:

            # --- Load selected city by its name 
            self.carlaWorld = self.carlaClient.load_world(self.carlaMap)

            settings = self.carlaWorld.get_settings()

            settings.synchronous_mode = False

            self.carlaWorld.apply_settings(settings)

            # --- Load blue-print library
            self.carlaBlueprintLibrary = self.carlaWorld.get_blueprint_library()

            # --- Get default vehicles list for selected city
            self.carlaVehicles = self.carlaBlueprintLibrary.filter('vehicle.*.*')

            self.carlaTrafficManager = self.carlaClient.get_trafficmanager(self.app_settings.carlaServerTrafficManagerPort)
            self.carlaTrafficManager.set_synchronous_mode(False)

            #spawn_points = self.carlaWorld.get_map().get_spawn_points()
            self.world_spawn_points = self.carlaWorld.get_map().get_spawn_points()

            self.setMode(True)

            if self.app_settings.carlaServerUseTrafficManager == True:

                self.generateTrafficVehicles(self.app_settings.carlaServerTrafficManagerRequiredVehicles)
                self.generateTrafficPedestrians(self.app_settings.carlaServerTrafficManagerRequiredPedestrians)

                description = "{} vehicles generated ({} - collision error), {} walkers generated ({} - collision error)".format(
                    self.spawned_generated_vehicles, self.spawned_non_generated_vehicles,
                    self.spawned_generated_walkers, self.spawned_non_generated_walkers)

                # --- Prepare collsions conditions
                self.carlaTrafficManager.set_hybrid_physics_mode(self.app_settings.useHybridPhysicsMode)

                if self.app_settings.useHybridPhysicsMode == True:
                    self.carlaTrafficManager.set_hybrid_physics_radius(self.app_settings.hybridModeRadius)

            else: 
                description = "Traffic generation is not requested"

            # --- Set predefined weather conditions ---
            weather = carla.WeatherParameters(
                cloudiness = float(self.app_settings.cloudiness),
                precipitation = float(self.app_settings.precipitation),
                precipitation_deposits = float(self.app_settings.road_water),
                wind_intensity = float(self.app_settings.wind_intensity),
                sun_azimuth_angle = float(self.app_settings.sun_azimuth_angle),
                sun_altitude_angle = float(self.app_settings.sun_altitude_angle),
                fog_density = float(self.app_settings.fog_density),
                fog_distance = float(self.app_settings.fog_distance),
                fog_falloff = float(self.app_settings.fog_falloff),
                scattering_intensity = float(self.app_settings.scattering_intensity),
                mie_scattering_scale = float(self.app_settings.mie_scattering_scale),
                #rayleigh_scattering_scale = self.app_settings.rayleigh_scattering_scale,
                wetness = float(self.app_settings.wetness),
                dust_storm = float(self.app_settings.dust_storm))
            
            self.carlaWorld.set_weather(weather)

            # --- Create traffic processor manager
            self.trafficScenarioProcessor = TrafficScenarioProcessor(self.carlaWorld)

        except Exception as e:

            error = str(e)
            description = "Error loading requested world"
            result = False        
            print(e)

        if self.onLoadWorldAttemptCompleted is not None:

            self.onLoadWorldAttemptCompleted(result, self.carlaVehicles, error,
                description)

    # --- CARLA spawning actor thread executor
    # --- actor: CARLA actor to be spawned
    # --- actorKind: CARLA actor to be spawned kind
    # --- behaviorName: vehicle behaviour profile name
    # --- extraParam: first extra parameter for a call (if any)
    # --- extraParam2: second extra parameter for a call (if any)
    # --- extraParam3: third extra parameter for a call (if any)
    def carlaSpawningActorThreadExecutor(self, actor, actorKind, behaviorName = None,
                                         extraParam = None, extraParam2 = None, 
                                         extraParam3 = None,
                                         ignoreTrafficLights = False,
                                         ignoreStopSigns = False,
                                         ignoreVehicles = False):

        result = True
        error = ""

        try:

            match actorKind:
                
                case CarlaActor.Vehicle:

                    requestedVehicle = self.FindVehicle(actor.BlueprintID)                    

                    start_point = random.randint(0, len(self.world_spawn_points) - 1)

                    spawn_point = self.world_spawn_points[start_point]

                    del self.world_spawn_points[start_point]

                    #requestedVehicle.set_attribute('role_name', 'hero')

                    vehicle = self.carlaWorld.spawn_actor(
                        requestedVehicle, spawn_point)

                    # --- Check max steering wheel angles
                    physics_control = vehicle.get_physics_control()

                    for wheel in physics_control.wheels:
                        print (wheel.max_steer_angle)

                    # -----------------------------------

                    #vehicle.set_attribute('role_name', 'autopilot')

                    self.spawned_vehicles.append(
                        SpawnedVehicleItem(vehicle, actor, requestedVehicle, behaviorName,
                                           ignoreTrafficLights, ignoreStopSigns, ignoreVehicles))
                
                    # --- Process spawning vehicle' video cams

                    for videocam in actor.InstalledVideoCams:

                        if self.carlaSpawningActorThreadExecutor(videocam, CarlaActor.VideoCam, None,
                            vehicle, actor, videocam) == False:
                                break

                    if self.onActorHasBeenSpawned is not None:
                        self.onActorHasBeenSpawned(result, None, error)

                case CarlaActor.VideoCam:

                    if extraParam is not None:
                        self.spawnVideoSensor(actor, extraParam, extraParam2, True)

        except Exception as e:

            error = str(e)
            result = False        
            print(e)
            if self.onActorHasBeenSpawned is not None:
                self.onActorHasBeenSpawned(result, None, error)

    # --- Start vehicle manual control thread executor routine
    def carlaStartVehicleThreadExecutor(self):

        result = True
        error = ""

        try:        
           
            print("------- Behavior: {}".format(self.selected_spawned_vehicle.behaviorName))
            print("------- Ignore lights: {}".format(self.selected_spawned_vehicle.ignore_traffic_lights))
            print("------- Ignore stops: {}".format(self.selected_spawned_vehicle.ignore_stop_signs))
            print("------- Ignore vehicles: {}".format(self.selected_spawned_vehicle.ignore_vehicles))

            controlledVehicle = BehaviorAgent(self.selected_spawned_vehicle.carlaVehicleObj,
                                              self.selected_spawned_vehicle.behaviorName) 
            
            controlledVehicle.ignore_traffic_lights(active=self.selected_spawned_vehicle.ignore_traffic_lights == 1)
            controlledVehicle.ignore_stop_signs(active=self.selected_spawned_vehicle.ignore_stop_signs == 1)
            controlledVehicle.ignore_vehicles(active=self.selected_spawned_vehicle.ignore_vehicles == 1)

            self.vehicles_under_autopilot.append(
                ControlledVehicleItem(self.selected_spawned_vehicle.ownVehicleObj.Uuid,
                                  controlledVehicle, True))

            #self.trafficScenarioProcessor.createTrafficVehicle(
            #    "Leader", self.selected_spawned_vehicle.carlaVehicleObj, 
            #    self.carlaVehicles, 0, 10)

            #self.trafficScenarioProcessor.createTrafficVehicle(
            #    "Follover", self.selected_spawned_vehicle.carlaVehicleObj, 
            #    self.carlaVehicles, 180, 10)

        except Exception as e:

            error = str(e)
            result = False        
            print(e)

        if result == True:
            if self.onVehicleHasBeenStarted is not None:
                self.onVehicleHasBeenStarted(result, error)

    # --- CARLA simulator syncronization thread (ticks issuer) 
    def carlaSyncTickThreadExecutor(self):

        while self.stopSyncThreadRequest == False:

            try:

                self.carlaWorld.tick()

                index = 0

                for sensor in self.activeSensors:
                    sensor.OnNewCarlaFrameReceived()
                    # --- Update autopiloted vehicles 
                    self.updateAutopilotDrivenVehiclesMoving(self.vehicles_under_autopilot, True)
                    index = index + 1

                if self.selected_controlled_vehicle is not None:
                    vehicles = []
                    vehicles.append(self.selected_controlled_vehicle)
                    self.updateAutopilotDrivenVehiclesMoving(vehicles, False)

                # --- Check signals from pedestrians phones
                self.ProcessPedestriansPositions()

                #self.GetActorsInRoles("hero")

            except Exception as e:

                print("Error in main cycle: {}".format(e))

        print("*** MAIN TICK THREAD IS STOPPED")

        self.stopSyncThreadRequest = False

    #---------------------------------
    #--- Public methods (services) ---
    #---------------------------------

    # --- Set CARLA simulator general mode
    # --- useSettings: use application settings to define requested mode
    def setMode(self, useSettings = False):

        mode = 0

        if useSettings == True:

            if self.app_settings.carlaServerGeneralMode == 0:

                if self.app_settings.carlaServerRequiredFps == -1:
                    mode = 1
                else:
                    mode = 2
            else:
                if self.app_settings.carlaServerRequiredFps == -1:
                    mode = 3
                else:
                    mode = 4

        requestSync = False;

        if self.carlaWorld is not None:
        
            settings = self.carlaWorld.get_settings()

            match mode:
                case 1:
                    settings.synchronous_mode = False
                    settings.fixed_delta_seconds = None
                case 2:
                    settings.synchronous_mode = False
                    settings.fixed_delta_seconds = 1 / self.app_settings.carlaServerRequiredFps
                    requestSync = True
                case 3:
                    settings.synchronous_mode = True
                    settings.fixed_delta_seconds = None
                    requestSync = True
                case 4:
                    settings.synchronous_mode = True
                    settings.fixed_delta_seconds = 1 / self.app_settings.carlaServerRequiredFps
                    requestSync = True

            self.carlaWorld.apply_settings(settings)

            self.carlaClient.reload_world(False)

            if self.carlaTrafficManager is not None:
                self.carlaTrafficManager.set_synchronous_mode(requestSync)

            if requestSync == True:
                self.stopSyncThreadRequest = False
                self.carlaSyncThread = threading.Thread(target=self.carlaSyncTickThreadExecutor, 
                                                     daemon=True)
                self.carlaSyncThread.start()
            else:
                self.stopSyncThreadRequest = True

    # --- Set currently selected spawned vehicle
    # --- uuid: requested spawned vehicle Uuid
    # --- isControlled: if true set constolled vehicle, set spawned if false
    def SetSelectedVehicle(self, uuid, isControlled):

        if isControlled == True:
            if uuid is None:
                if self.selected_controlled_vehicle is not None:
                    # --- RESPAWN
                    self.RespawnEgoVehicle(self.selected_controlled_vehicle, 'autopilot')

                    #self.selected_controlled_vehicle.carlaBlueprintObj.set_attribute('role_name', '')
                    uuid1 = self.selected_controlled_vehicle.ownVehicleObj.Uuid
                    self.selected_controlled_vehicle = None
                    indexSensor = 0

                    for activeSensor in self.activeSensors:
                    
                        if uuid1 == activeSensor.params.parentVehicleUuid:
                            if self.onMovingStep is not None:
                                mparam = MovingParamsItem(indexSensor, 
                                    None, None, None, None, None)
                                self.onMovingStep(mparam)
                        indexSensor = indexSensor + 1
            else:
                controlled_vehicle = self.obtainSelectedSpawnedVehicle(uuid)
                self.RespawnEgoVehicle(controlled_vehicle, 'hero')
                self.selected_controlled_vehicle = controlled_vehicle
        else:
            self.selected_spawned_vehicle = self.obtainSelectedSpawnedVehicle(uuid)

        if self.selected_spawned_vehicle is not None:
            print(self.selected_spawned_vehicle.ownVehicleObj.Name)

    # --- Obtain currently spawned vehicle full description by its UUID
    # --- uuid: UUID to search for
    def obtainSelectedSpawnedVehicle(self, uuid):

        for vehicle in self.spawned_vehicles:
            if vehicle.ownVehicleObj.Uuid == uuid:
                return vehicle
        return None
       
    # --- Perform vehicle movement action
    # --- action: action to be performed
    # --- param: action parameter
    # --- param2: action extra parameter (if any)
    def DoAction(self, action, param, param2 = None):

        if self.carlaClient is not None:
        
            if self.selected_controlled_vehicle is not None:

                control = self.selected_controlled_vehicle.carlaVehicleObj.get_control()

                match action:
                    case 1:
                        print("Turn angle: {}".format(param))
                        # Set the steering angle (e.g., turn right)
                        control.steer = param  # Adjust as needed

                    case 2:    
                        print("Throttle value: {}".format(param))
                        control.throttle = param

                    case 3:    
                        print("Braking value: {}".format(param))
                        control.brake = param

                    case 4:
                        control.manual_gear_shift = param == 1
                        control.gear = param2

                    case 5:
                        control.gear = param

                    case 6:
                        control.hand_brake = param == 1

                    case 7:
                        control.manual_gear_shift = True
                        control.gear = param2
                        control.reverse = param == 1

                if self.selected_controlled_vehicle is not None:
                    # Apply the control to the vehicle
                    self.selected_controlled_vehicle.carlaVehicleObj.apply_control(control)               

    check = False

    # --- Sensors data receiver callback
    # --- data: received data package
    # --- uuid: sensor receiver UUID    
    def sensor_callback(self, data, uuid): 

        if self.check == True:
            return

        self.check = True

        index = self.getSpawnedSensorIndex(uuid)

        print("RECEIVED FRAME FOR SENSOR: {}".format(uuid))

        if index != -1:
            self.activeSensors[index].frames_queue.put((data, uuid))

        self.check = False

    # --- Stop sensors 
    def StopThreads(self):

        # --- Destroy CARLA connected objects    

        try:

            for sensor in self.activeSensors:
                if sensor.Sensor.is_alive == True:
                    if sensor.Sensor.is_listening() == True:
                        print("Stop listening sensor")
                        sensor.Sensor.stop()
                    print("Destroying sensor")
                    sensor.Sensor.destroy()

            for vehicle in self.spawned_vehicles:
                if vehicle.carlaVehicleObj.is_alive == True:
                    print("Destroying vehicle")
                    vehicle.carlaVehicleObj.destroy()

            if self.carlaClient is not None:
                # --- Destroy traffic vehicles if exists
                self.carlaClient.apply_batch([carla.command.DestroyActor(x) for x in self.traffic_objects_list])
                self.carlaClient.apply_batch([carla.command.DestroyActor(x) for x in self.all_id])

        except Exception as e:

            print(e)

        self.setMode()

    #---------------------------------

    #------------------------------------------
    # --- Traffic generation implementation ---
    # -----------------------------------------

    # --- Generate set of traffic vehicles
    # --- requestedCount: requested vehicles count value
    def generateTrafficVehicles(self, requestedCount):

        self.spawned_generated_vehicles = 0
        self.spawned_non_generated_vehicles = 0

        # --------------
        # Spawn vehicles
        # --------------
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        batch = []

        for n, transform in enumerate(self.world_spawn_points):

            if n >= requestedCount:
                break

            start_point = random.randint(0, len(self.world_spawn_points))
            transform = self.world_spawn_points[start_point]
            print("Len1: {}".format(len(self.world_spawn_points)))
            del self.world_spawn_points[start_point]
            print("Len2: {}".format(len(self.world_spawn_points)))

            blueprint = random.choice(self.carlaVehicles)

            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            
            blueprint.set_attribute('role_name', 'autopilot')

            # spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, 
                    self.carlaTrafficManager.get_port())))

        self.carlaWorld.tick()

        for response in self.carlaClient.apply_batch_sync(batch, self.app_settings.carlaServerGeneralMode == 1):
            if response.error:
                print(response.error)
                self.spawned_non_generated_vehicles = self.spawned_non_generated_vehicles + 1
            else:
                self.traffic_objects_list.append(response.actor_id)
                self.spawned_generated_vehicles = self.spawned_generated_vehicles + 1

    # --- Generate set of traffic pedestrians
    # --- requestedCount: requested pedestrians count value
    def generateTrafficPedestrians(self, requestedCount):
        
        self.spawned_generated_walkers = 0
        self.spawned_non_generated_walkers = 0

        SpawnActor = carla.command.SpawnActor

        percentagePedestriansRunning = 0.0      # how many pedestrians will run
        percentagePedestriansCrossing = 0.0     # how many pedestrians will walk through the road

        blueprintsWalkers = self.carlaWorld.get_blueprint_library().filter("walker*.*")

        # 1. take all the random locations to spawn
        spawn_points = []
        for i in range(requestedCount):

            spawn_point = carla.Transform()
            loc = self.carlaWorld.get_random_location_from_navigation()
            print("Loc: {}".format(loc))
            if (loc != None):
                spawn_point.location = loc
                spawn_points.append(spawn_point)

        # 2. we spawn the walker object
        batch = []
        walker_speed = []
        walker_speed2 = []
        i = 0

        while True:

            walker_bp = random.choice(blueprintsWalkers)
            
            spawned_walker = self.carlaWorld.try_spawn_actor(walker_bp, spawn_points[i])

            if spawned_walker is None:
                loc = self.carlaWorld.get_random_location_from_navigation()
                if (loc != None):
                    spawn_points[i].location = loc
                continue

            # set as not invincible
            if walker_bp.has_attribute('is_invincible'):
                walker_bp.set_attribute('is_invincible', 'false')
            # set the max speed
            if walker_bp.has_attribute('speed'):
                if (random.random() > percentagePedestriansRunning):
                    # walking
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
                else:
                    # running
                    walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
            else:
                print("Walker has no speed")
                walker_speed.append(0.0)

            self.generated_pedestrians.append(spawned_walker)

            self.walkers_list.append({"id": spawned_walker.id})
            self.spawned_generated_walkers = self.spawned_generated_walkers + 1
            i = i + 1
            if i > (len(spawn_points) - 1):
                break

        # 3. we spawn the walker controller
        batch = []
        walker_controller_bp = self.carlaWorld.get_blueprint_library().find('controller.ai.walker')

        for i in range(len(self.walkers_list)):
            batch.append(SpawnActor(walker_controller_bp, 
                                    carla.Transform(), self.walkers_list[i]["id"]))
        results = self.carlaClient.apply_batch_sync(batch, True)

        for i in range(len(results)):
            if results[i].error:
                print("Error2: ".format(results[i].error))
            else:
                self.walkers_list[i]["con"] = results[i].actor_id

        # 4. we put together the walkers and controllers id to get the objects from their id
        for i in range(len(self.walkers_list)):
            self.all_id.append(self.walkers_list[i]["con"])
            self.all_id.append(self.walkers_list[i]["id"])
  
        all_actors = self.carlaWorld.get_actors(self.all_id)

        # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
        # set how many pedestrians can cross the road
        self.carlaWorld.set_pedestrians_cross_factor(percentagePedestriansCrossing)

        print("BEFORE START WALKERS")

        for i in range(0, len(self.all_id), 2):

            try:
                # start walker
                all_actors[i].start()
                # set walk to random point
                all_actors[i].go_to_location(self.carlaWorld.get_random_location_from_navigation())
                # max speed
                all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))
            except Exception as e:
                self.spawned_non_generated_walkers = self.spawned_non_generated_walkers + 1
                print("Error start walker: {}".format(e))

        # Example of how to use Traffic Manager parameters
        self.carlaTrafficManager.global_percentage_speed_difference(70.0)

        print("Success!")

    # -----------------------------------------------------

    # --- Find sensor index in spawned ones collection by its GUID
    # --- GUID to be found
    def getSpawnedSensorIndex(self, uuid):
    
        i = 0

        for s in self.activeSensors:

            if uuid == s.params.parentUuid:
                return i

            i = i + 1

    # --- Hide parent progress window if specified
    def hideProgressWindow(self):

        print("******* Hide progress window")

        if self.progressWnd is not None:

            self.progressWnd.hide()

        self.progressWnd = None

    # --- Make moving step for autopilot driven vehicles
    def updateAutopilotDrivenVehiclesMoving(self, vehicles, applyControl):

        index = 0

        for vehicle in vehicles:

            if index == self.stopped_index:
                
                vehicle.controlledVehicle._vehicle.apply_control(vehicle.controlledVehicle.emergency_stop())
                self.vehicles_under_autopilot.remove(vehicle)
                self.stopped_index = -1
                indexSensor = 0
                for activeSensor in self.activeSensors:
                    
                    mparam = None

                    if vehicle.parentUuid == activeSensor.params.parentVehicleUuid:

                        if self.onMovingStep is not None:
                            mparam = MovingParamsItem(indexSensor, 
                                None, None, None, None, None)

                            self.onMovingStep(mparam)

                    indexSensor = indexSensor + 1
            else:

                if applyControl:
                    if vehicle.isMoving == True:
                        vehicle.controlledVehicle._vehicle.apply_control(vehicle.controlledVehicle.run_step())

                indexSensor = 0

                # --- ! CHECK IS SENSOR FOR RUNNING VEHICLE
                for activeSensor in self.activeSensors:
                    
                    mparam = None

                    proceed = False

                    if applyControl == True:
                        proceed = vehicle.parentUuid == activeSensor.params.parentVehicleUuid
                    else:
                        proceed = vehicle.ownVehicleObj.Uuid == activeSensor.params.parentVehicleUuid

                    if proceed:
                        
                        if self.onMovingStep is not None:

                            mparam = None

                            if applyControl == True:
                                mparam = MovingParamsItem(indexSensor, vehicle.controlledVehicle._speed, 
                                              vehicle.controlledVehicle._vehicle.get_velocity().length(),
                                              vehicle.controlledVehicle._vehicle.get_acceleration(),
                                              vehicle.controlledVehicle._vehicle.get_angular_velocity(), 
                                              vehicle.controlledVehicle._vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FL_Wheel))
                            else:
                                mparam = MovingParamsItem(indexSensor, vehicle.carlaVehicleObj.get_velocity().length() * 3.6, 
                                              vehicle.carlaVehicleObj.get_velocity().length(),
                                              vehicle.carlaVehicleObj.get_acceleration(),
                                              vehicle.carlaVehicleObj.get_angular_velocity(), 
                                              vehicle.carlaVehicleObj.get_wheel_steer_angle(carla.VehicleWheelLocation.FL_Wheel))

                            self.onMovingStep(mparam)
                    else:
                        mparam = MovingParamsItem(indexSensor, 
                            None, None, None, None, None)

                    indexSensor = indexSensor + 1
            
            index = index + 1

    # --- Place obstacle on the way on specified vehicle
    # --- vehicleId: vehicle for which we emulate obstacle identifier
    # --- obstacleKind: kind of obstacle to be emulated name
    # --- distance: distance from vehicle to spawn obstacle (meters) 
    # --- angle: direction from vehicle to spawn obstacle (degrees)
    # --- isMoving: if true move obstacle object, do not move if false
    def EmulateObstacle(self, vehicleId, obstacleKind, distance, angle, isMoving):

        try:

            #self.GetAnotherClientsHeroes("hero")

            if len(self.spawned_vehicles) > 0:

                obstacleObj = None

                spawn_point = TrafficScenarioProcessor.GetVehiclePosition(self.spawned_vehicles[vehicleId - 1].carlaVehicleObj, 
                    distance, angle)

                if spawn_point is not None:

                    match obstacleKind:
                        case "vehicle":
                            obstacleVehicle = random.choice(self.carlaVehicles)
                            if obstacleVehicle.has_attribute('color'):
                                color = random.choice(obstacleVehicle.get_attribute('color').recommended_values)
                                obstacleVehicle.set_attribute('color', color)

                            obstacleObj = self.carlaWorld.spawn_actor(
                                obstacleVehicle, spawn_point)

                            controlledVehicle = BehaviorAgent(obstacleObj, "normal")

                            self.vehicles_under_autopilot.append(
                                ControlledVehicleItem("", controlledVehicle, isMoving))

                    return ""

                else:

                    err = "No suitable spawn points are found"

                    print(err)

                    return err
    
            else:

                return "No spawned vehicles yet"
        
        except Exception as ex:

            err = "Error setting obstacle: {}".format(ex)

            print(err)
            
            return err

    # --- Get list of all actors, which belong to specified role
    # roleName: requested role name
    def GetActorsInRoles(self, roleName):

        vehicles = self.carlaWorld.get_actors().filter('*vehicle*')

        actors = []

        count = 0

        for vehicle in vehicles:
            count = count + 1
            if vehicle.attributes['role_name'] == roleName:
                print("------- Role {} is found".format(roleName))
                actors.append(vehicle)

            print("VEHICLE ROLE NAME: {}".format(vehicle.attributes['role_name']))

        print("Actors checked: {}".format(count))

        return actors

    # --- Respawn vehicle which is requested as ego (to set role name correctly)
    # --- vehicle: vehicle object to be respawned
    # --- role_name: required role name to be set
    def RespawnEgoVehicle(self, vehicle, role_name):
        
        try:
            # --- Get vehicle position
            current_position = vehicle.carlaVehicleObj.get_transform()
            current_position.location.z += 1

            # --- Destroy vehicle
            vehicle.carlaVehicleObj.destroy()
         
            # --- Get new blueprint
            requestedVehicle = vehicle.carlaBlueprintObj

            # --- Set role name 'hero'
            requestedVehicle.set_attribute('role_name', role_name)

            while True:
                try:
                    # --- Spawn again at saved position
                    spawned_vehicle = self.carlaWorld.spawn_actor(
                        requestedVehicle, 
                        current_position)
                    break
                except Exception as e:
                    current_position.location.z += 1

            # --- Respawn video sensors
            for sensor in self.activeSensors:
                if vehicle.ownVehicleObj.Uuid == sensor.params.parentVehicleUuid:
                    # Stop old sensor listener
                    # Check how many video streams
                    # check "hero" role exists 
                    sensor.Sensor.stop()
                    sensor.Sensor.destroy()
                    spawnedSensor = self.spawnVideoSensor(
                        sensor.params.ownSensor, spawned_vehicle, vehicle.ownVehicleObj, False)
                    sensor.Sensor = spawnedSensor

            # --- Update application object properties 
            # --- (currently_selected_vehicle.carlaVehicleObj
            # --- with new spawned object)
            vehicle.carlaVehicleObj = spawned_vehicle

        except Exception as ex:
            print("Error respawning vehicle: {}".format(ex))

    # ===============================================
    # ===           VEHICLE CONTROL UNIT         ====
    # ===============================================

    # --- Connect to vehicle control unit 
    # --- host: vehicle control unit address (Dns name)
    # --- port: vehicle control unit port
    def ConnectVCU(self, host, port):

        self.vcu_Connector = VehicleControlUnitConnector("<hhhhhBB")

        if self.onControlUnitConnectionAttemptCompleted is not None:
            if self.vcu_Connector.connect(host, port) == True:
                self.onControlUnitConnectionAttemptCompleted(True)
            else:
                self.onControlUnitConnectionAttemptCompleted(False)
            self.vcu_Connector.OnDataPackageReceived = self.OnVehicleControlReceived
        else:
            self.vcu_Connector = None

    # --- Disconnect from vehicle control unit 
    def DisconnectVCU(self):

        self.vcu_Connector.disconnect()
        self.vcu_Connector = None

    # --- Connect to prediction unit 
    # --- host: prediction device address (Dns name)
    # --- port: prediction device port
    # --- Enter after the ConnectTPU button is pressed
    def ConnectTPU(self, host, port):

        print("[carla processor] Connecting to TPU: {}:{}".format(host, port))
        self.tpu_Connector = PredictionUnitConnector(self)

        if self.onPredictionUnitConnectionAttemptCompleted is not None:
            if self.tpu_Connector.connect(host, port) == True:
                print("[carla processor] Connected to TPU: {}:{}".format(host, port))
                for sensor in self.activeSensors:
                    sensor.predictionUnitService = self.tpu_Connector
                self.onPredictionUnitConnectionAttemptCompleted(True)
                print("[carla processor] TPU connection attempt completed")
            else:
                print("[carla processor] Failed to connect to TPU: {}:{}".format(host, port))
                self.onPredictionUnitConnectionAttemptCompleted(False)
                for sensor in self.activeSensors:
                    sensor.predictionUnitService = None
        else:
            self.tpu_Connector = None

    # --- Disconnect from prediction unit 
    def DisconnectTPU(self):

        self.tpu_Connector.disconnect()
        self.tpu_Connector = None

    # --- Vehicle control data package is received event handler
    # --- dataPackage: received data package (bytes array) 
    def OnVehicleControlReceived(self, dataPackage):

        print("[carla processor] Raw data received: {}".format(dataPackage))
        self.DoActionFromVCU(dataPackage, ControlDataPackageItem(dataPackage))

    # --- Perform vehicle movement action
    # rawData: data package received from VCU
    # dataPackage: converted VCU data package to be applied 
    def DoActionFromVCU(self, rawData, dataPackage):

        if self.carlaClient is not None:
        
            if self.selected_controlled_vehicle is not None:

                control = self.selected_controlled_vehicle.carlaVehicleObj.get_control()

                control.steer = dataPackage.wheelAngle
                control.throttle = dataPackage.acceleratorPosition
                control.brake = dataPackage.brakePosition
                #control.manual_gear_shift = dataPackage.gearPosition == 1
                #control.gear = dataPackage.gearPosition

                if self.selected_controlled_vehicle is not None:
                    # Apply the control to the vehicle
                    self.selected_controlled_vehicle.carlaVehicleObj.apply_control(control)               

        if self.OnVehicleControlMessageReceived is not None:
            self.OnVehicleControlMessageReceived(rawData, dataPackage)

    # --- Find Carla vehicle object by its blueprint ID
    # blueprintID: requested blueprint ID
    def FindVehicle(self, blueprintID):
        
        requestedVehicle = None

        for vehicle in self.carlaVehicles:
            if vehicle.id == blueprintID:
                requestedVehicle = vehicle
                return requestedVehicle

        return None

    # --- Spawn video sensor
    # actor: video sensor object (application specific)
    # parentCarlaObj: parent vehicle (spawned Carla object)
    # parentOwnObj: parent vehicle (application specific)
    # addToList: add spawned sensor to active sensors list flag

    # https://carla.readthedocs.io/en/0.8.4/cameras_and_sensors/#camera-semantic-segmentation

    def spawnVideoSensor(self, actor, parentCarlaObj, parentOwnObj, addToList):

        blueprint = self.carlaWorld.get_blueprint_library().find('sensor.camera.rgb')
  
        # Modify the attributes of the blueprint to set image resolution and field of view.
        blueprint.set_attribute('image_size_x', str(actor.frameSizeX))
        blueprint.set_attribute('image_size_y', str(actor.frameSizeY))
        blueprint.set_attribute('fov', str(actor.fieldOfVision))
        blueprint.set_attribute('sensor_tick', '0.0')
                        
        # Provide the position of the sensor relative to the vehicle.
        transform = carla.Transform(
            carla.Location(x=actor.position.positionX, 
                y=actor.position.positionY, z=actor.position.positionZ), 
                carla.Rotation(yaw=actor.rotationYaw))

        blueprint.set_attribute('ros_name', actor.name)

        spawnedSensor = self.carlaWorld.spawn_actor(
            blueprint, transform, parentCarlaObj)

        spawnedSensor.enable_for_ros()

        if addToList:
            spawnedSensorParams = SpawnedSensorParamItem(
                actor.frameSizeX / actor.frameSizeY,
                "{} ({} / {})".format(parentOwnObj.Name, parentOwnObj.Manufacturer, parentOwnObj.Model),
                actor.name, actor.Uuid,
                actor.frameSizeX, actor.frameSizeY, 
                parentOwnObj.Uuid, actor)

            spawned_sensor_item = SpawnedSensorItem(
                spawnedSensor, len(self.activeSensors), 
                self.onNewVideoFrameIsRecieved, 
                spawnedSensorParams, self.app_settings,
                len(self.activeSensors), self)

            self.activeSensors.append(spawned_sensor_item)

        if self.app_settings.carlaServerGeneralMode == 0:
            spawnedSensor.listen(lambda data: spawned_sensor_item.OnNewCarlaFrameReceived(data, actor.Uuid))
        else:
            spawnedSensor.listen(lambda data: self.sensor_callback(data, actor.Uuid))

        return spawnedSensor

    # --- Unspawn selcted vehicle 
    # vehicle: vehicle to be unspawned
    def UnspawnVehicle(self, vehicle):

        try:
            for v in self.spawned_vehicles:
                if vehicle.Uuid == v.ownVehicleObj.Uuid: 
                # --- Respawn video sensors
                    for sensor in self.activeSensors:
                        if vehicle.ownVehicleObj.Uuid == sensor.params.parentVehicleUuid:
                            sensor.Sensor.stop()
                            sensor.Sensor.destroy()

                vehicle.carlaVehicleObj.destroy()
        except Exception as ex:
            print("Error unspawning vehicle: {}".format(ex))
                
    # --- Prediction unit reply is received
    # processedImage: image processed by prediction unit
    def PredictionUnitReplyReceived(self, raw_data, processedImage, ratio):
        if self.onPredictionUnitReplyReceived is not None:
            self.onPredictionUnitReplyReceived(raw_data, processedImage, ratio)

    # --- Get spawn point which is closest to provided one
    # position: point to be checked
    def GetClosestSpawnPointIndex(self, position):

        index_of_min = 0

        current_index = 0

        minimum = sys.float_info.max

        for spawn_point in self.world_spawn_points:
            
            distance = spawn_point.location.distance(position)
            
            if distance < minimum:
                index_of_min = current_index
                minimum = distance 

            current_index = current_index + 1

        return index_of_min

    # --- Process signals from pedestrians phones
    def ProcessPedestriansPositions(self):

        if self.selected_controlled_vehicle is not None:
        
            base_location = self.selected_controlled_vehicle.carlaVehicleObj.get_transform().location

            if self.generated_pedestrians is not None:

                index = 1

                for p in self.generated_pedestrians:
                    
                    plocation = p.get_transform().location 

                    distance = plocation.distance(
                        base_location)
            
                    dx = plocation.x - base_location.x
                    dy = plocation.y - base_location.y

                    # Calculate the angle in radians
                    angle_rad = math.atan2(dx, dy)

                    # Convert to degrees
                    angle_deg = math.degrees(angle_rad)

                    # Normalize to 0-360 degrees
                    azimuth = (angle_deg + 360) % 360

                    print("Pedestrian {0} location: {1:.1f} m / {2:.1f} degrees".format(
                        index, distance, azimuth))
                
                    index = index + 1


    # === SPECTATOR TOP-DOWN VIEW IMPLEMENTATION ===

    # --- Start top-down sensor
    def startTopDownSensor(self):
        
        if self.selected_controlled_vehicle is not None:
            
            print("Start top-down view process")
          
            blueprint = self.carlaWorld.get_blueprint_library().find('sensor.camera.instance_segmentation')

            transform = carla.Transform(
                carla.Location(x=1.5, y=0, z=25), 
                    carla.Rotation(pitch=-90))
            
            self.topDownSensor = self.carlaWorld.spawn_actor(
                blueprint, transform, 
                self.selected_controlled_vehicle.carlaVehicleObj)

            self.topDownSensor.listen(
                lambda data: self.top_down_sensor_callback(data))

    # --- Stop top-down sensor
    def stopTopDownSensor(self):

        if self.topDownSensor is not None:
            self.topDownSensor.stop()
            self.topDownSensor.destroy()
            self.topDownSensor = None
    
    # --- Top-down sensor listen callback
    # --- data: receieved image
    def top_down_sensor_callback(self, data):
        
        if data is not None:
            print("==============******* Top down image received")
            if self.OnTopDownImageReceived is not None:
                self.OnTopDownImageReceived(data)

    # ===============================================