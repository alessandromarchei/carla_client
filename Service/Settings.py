
#====================================================
# ===            CARLA emulator client            ===
# ===   ------------------------------------      ===
# ===  Application settings collection definition ===
#====================================================

import os
import json

class Settings_Set(object):
    
    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- Path to settings file
    path = ""

    # --- Remote Carla server URL address
    carlaServerUrl: None

    # --- Remote Carla server main connection port
    carlaServerMainPort = 0

    # --- Remote Carla server traffic manager service port
    carlaServerTrafficManagerPort = 0

    # --- Remote Carla server connection timeout (sec)
    carlaServerConnectionTimeout = 0

    # --- Remote Carla server general functional mode
    # --- (0 - asynchronous, 1 - synchronous)
    carlaServerGeneralMode = 0

    # --- Remote Carla server required max FPS
    carlaServerRequiredFps = -1

    # --- Max allowed frames queue size before recreation
    maxFramesQueueSize = 50

    # --- Timeout for frames queue operations (sec)
    queueGetActionTimeout = 10

    # --- Use remote Carla server traffic manager flag
    carlaServerUseTrafficManager = 0

    # --- Required count of generated traffic manager vehicles
    carlaServerTrafficManagerRequiredVehicles = 3

    # --- Required count of generated traffic manager pedestrians
    carlaServerTrafficManagerRequiredPedestrians = 3

    # --- Current weather conditions ---

    # --- Values range from 0 to 100, being 0 a clear sky and 100 one completely covered with clouds
    cloudiness = 0

    # --- Rain intensity values range from 0 to 100, being 0 none at all and 100 a heavy rain
    precipitation = 0

    # --- Determines the creation of puddles. Values range from 0 to 100, being 0 none at all and 100 a road completely capped with water
    road_water = 0

    # --- Controls the strenght of the wind with values from 0, no wind at all, to 100, a strong wind
    wind_intensity = 0

    # --- The azimuth angle of the sun. Values range from 0 to 360
    sun_azimuth_angle = 90

    # --- Altitude angle of the sun. Values range from -90 to 90 corresponding to midnight and midday each
    sun_altitude_angle = 90

    # --- Fog concentration or thickness. It only affects the RGB camera sensor. Values range from 0 to 100
    fog_density = 0

    # --- Fog start distance. Values range from 0 to infinite
    fog_distance = 0

    # --- Density of the fog (as in specific mass) from 0 to infinity. The bigger the value, the more dense and heavy it will be, and the fog will reach smaller heights
    fog_falloff = 0

    # --- Controls how much the light will contribute to volumetric fog. When set to 0, there is no contribution
    scattering_intensity = 0

    # --- Controls interaction of light with large particles like pollen or air pollution resulting in a hazy sky with halos around the light sources. When set to 0, there is no contribution
    mie_scattering_scale = 0

    # --- Controls interaction of light with small particles like air molecules. Dependent on light wavelength, resulting in a blue sky in the day or red sky in the evening
    rayleigh_scattering_scale = 0

    # --- Wetness intensity. It only affects the RGB camera sensor. Values range from 0 to 100
    wetness = 0

    # --- Determines the strength of the dust storm weather. Values range from 0 to 100
    dust_storm = 0

    # --- Use hybrid physics mode for Traffic Manager
    useHybridPhysicsMode = 0

    # --- Hybrid mode radius (meters)
    hybridModeRadius = 50

    # --- Vehicle control unit address (Dns name)
    vehicleControlUnitAddress = "192.168.50.1"
         
    # --- Vehicle control unit port
    vehicleControlUnitPort = 3333

    # --- Prediction unit address (Dns name)
    predictionUnitAddress = "192.168.1.14"
         
    # --- Prediction unit port
    predictionUnitPort = 1477

    # ----------------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- path: path to settings file
    # --- carlaServerUrl: Remote Carla server URL address
    # --- carlaServerMainPort: Remote Carla server main connection port
    # --- carlaServerTrafficManagerPort: Remote Carla server traffic manager service port
    # --- carlaServerConnectionTimeout: Remote Carla server connection timeout (sec)
    # --- carlaServerGeneralMode: Remote Carla server general functional mode
    # --- (0 - asynchronous, 1 - synchronous)
    # --- carlaServerRequiredFps: Remote Carla server required max FPS
    # --- maxFramesQueueSize: max allowed frames queue size before recreation
    # --- queueGetActionTimeout: timeout for frames queue operations (sec)
    # --- carlaServerUseTrafficManager: use remote Carla server traffic manager flag
    # --- carlaServerTrafficManagerRequiredVehicles: required count of generated traffic manager vehicles
    # --- carlaServerTrafficManagerRequiredPedestrians: required count of generated traffic manager pedestrians
    def __init__(self, path, 
                 carlaServerUrl = "localhost",
                 carlaServerMainPort = 2000,
                 carlaServerTrafficManagerPort = 2001,
                 carlaServerConnectionTimeout = 25,
                 carlaServerGeneralMode = 0,
                 carlaServerRequiredFps = -1,
                 maxFramesQueueSize = 50,
                 queueGetActionTimeout = 10,
                 carlaServerUseTrafficManager = False,
                 carlaServerTrafficManagerRequiredVehicles = 3,
                 carlaServerTrafficManagerRequiredPedestrians = 3,
                 cloudiness = 0,
                 precipitation = 0,
                 road_water = 0,
                 wind_intensity = 0,
                 sun_azimuth_angle = 90,
                 sun_altitude_angle = 90,
                 fog_density = 0,
                 fog_distance = 0,
                 fog_falloff = 0,
                 scattering_intensity = 0,
                 mie_scattering_scale = 0,
                 rayleigh_scattering_scale = 0,
                 wetness = 0,
                 dust_storm = 0,
                 useHybridPhysicsMode = False,
                 hybridModeRadius = 50,
                 vehicleControlUnitAddress = "192.168.50.1",
                 vehicleControlUnitPort = 3333,
                 predictionUnitAddress = "192.168.50.1",
                 predictionUnitPort = 1477):
        
        self.path = path
        self.carlaServerUrl = carlaServerUrl 
        self.carlaServerMainPort = carlaServerMainPort
        self.carlaServerTrafficManagerPort = carlaServerTrafficManagerPort
        self.carlaServerConnectionTimeout = carlaServerConnectionTimeout
        self.carlaServerGeneralMode = carlaServerGeneralMode
        self.carlaServerRequiredFps = carlaServerRequiredFps
        self.maxFramesQueueSize = maxFramesQueueSize
        self.queueGetActionTimeout = queueGetActionTimeout
        self.carlaServerUseTrafficManager = carlaServerUseTrafficManager
        self.carlaServerTrafficManagerRequiredVehicles = carlaServerTrafficManagerRequiredVehicles
        self.carlaServerTrafficManagerRequiredPedestrians = carlaServerTrafficManagerRequiredPedestrians
        self.cloudiness = cloudiness
        self.precipitation = precipitation
        self.road_water = road_water
        self.wind_intensity = wind_intensity
        self.sun_azimuth_angle = sun_azimuth_angle
        self.sun_altitude_angle = sun_altitude_angle
        self.fog_density = fog_density
        self.fog_distance = fog_distance
        self.fog_falloff = fog_falloff
        self.scattering_intensity = scattering_intensity
        self.mie_scattering_scale = mie_scattering_scale
        self.rayleigh_scattering_scale = rayleigh_scattering_scale
        self.wetness = wetness
        self.dust_storm = dust_storm
        self.useHybridPhysicsMode = useHybridPhysicsMode
        self.hybridModeRadius = hybridModeRadius
        self.vehicleControlUnitAddress = vehicleControlUnitAddress
        self.vehicleControlUnitPort = vehicleControlUnitPort
        self.predictionUnitAddress = predictionUnitAddress
        self.predictionUnitPort = predictionUnitPort

    #-----------------------
    #--- Public methods  ---
    #-----------------------
    
    # --- Deserialize Xml node into vehicle object
    # --- item: Xml node to be deserialized
    def deserialize(self):

        try:

            if (os.path.exists(self.path)):

                with open(self.path) as f:
                    jsondata = f.read()
            
                decoded = Settings_Set(**json.loads(jsondata))

                self.carlaServerUrl = decoded.carlaServerUrl
                self.carlaServerMainPort = decoded.carlaServerMainPort
                self.carlaServerTrafficManagerPort = decoded.carlaServerTrafficManagerPort
                self.carlaServerConnectionTimeout = decoded.carlaServerConnectionTimeout
                self.carlaServerGeneralMode = decoded.carlaServerGeneralMode
                self.carlaServerRequiredFps = decoded.carlaServerRequiredFps
                self.maxFramesQueueSize = decoded.maxFramesQueueSize
                self.queueGetActionTimeout = decoded.queueGetActionTimeout

                self.carlaServerUseTrafficManager = decoded.carlaServerUseTrafficManager
                self.carlaServerTrafficManagerRequiredVehicles = decoded.carlaServerTrafficManagerRequiredVehicles
                self.carlaServerTrafficManagerRequiredPedestrians = decoded.carlaServerTrafficManagerRequiredPedestrians

                self.cloudiness = decoded.cloudiness
                self.precipitation = decoded.precipitation
                self.road_water = decoded.road_water
                self.wind_intensity = decoded.wind_intensity
                self.sun_azimuth_angle = decoded.sun_azimuth_angle
                self.sun_altitude_angle = decoded.sun_altitude_angle
                self.fog_density = decoded.fog_density
                self.fog_distance = decoded.fog_distance
                self.fog_falloff = decoded.fog_falloff
                self.scattering_intensity = decoded.scattering_intensity
                self.mie_scattering_scale = decoded.mie_scattering_scale
                self.rayleigh_scattering_scale = decoded.rayleigh_scattering_scale
                self.wetness = decoded.wetness
                self.dust_storm = decoded.dust_storm

                self.useHybridPhysicsMode = decoded.useHybridPhysicsMode
                self.hybridModeRadius = decoded.hybridModeRadius

                self.vehicleControlUnitAddress = decoded.vehicleControlUnitAddress
                self.vehicleControlUnitPort = decoded.vehicleControlUnitPort

                self.predictionUnitAddress = decoded.predictionUnitAddress
                self.predictionUnitPort = decoded.predictionUnitPort

                return True
        
        except Exception as e:

            print("Error reading settings: {}".format(e))
            return False


    # --- Serialize object to xml file
    # --- printXml: copy Xml to output window if true, otherwise false
    def serialize(self, printXml):

        try:

            jsondata = json.dumps(self.__dict__, 
                default=lambda o: o.__dict__, indent=4)
        
            if printXml == True:
                print(jsondata)

            # Write to Xml file
            with open(self.path, 'w') as f:
                f.write(jsondata);

        except Exception as e:

            print("Error writing settings: {}".format(e))
            return False

    # --- Create currently active weather description text
    def createWeatherDescription(self):

        res1 = "Clouds (%): {0:.0f}, ".format(float(self.cloudiness))
        res2 = "Precipitation (%): {0:.0f}, ".format(float(self.precipitation))
        res3 = "Water on roads (%): {0:.0f}, ".format(float(self.road_water))
        res4 = "Wind strenght (%): {0:.0f}, ".format(float(self.wind_intensity))
        res5 = "Sun azimuth angle (deg): {0:.0f}, ".format(float(self.sun_azimuth_angle))
        res6 = "Sun altitude angle (deg): {0:.0f}, ".format(float(self.sun_altitude_angle))
        res7 = "Fog density (%): {0:.0f}, ".format(float(self.fog_density))
        res8 = "Fog distance (m): {0:.0f}, ".format(float(self.fog_distance))
        res9 = "Fog falloff (m): {0:.0f}, ".format(float(self.fog_falloff))
        res10 = "Wetness intensity (%): {0:.0f}, ".format(float(self.wetness))
        res11 = "Dust storm strength (%): {0:.0f}".format(float(self.dust_storm))

        return "{}{}{}{}{}{}{}{}{}{}{}".format(
            res1, res2, res3, res4, res5, res6, res7, 
            res8, res9, res10, res11)
