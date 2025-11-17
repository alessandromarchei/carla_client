
#================================================
# ===           CARLA emulator client         ===
# ===   -----------------------------------   ===
# === Edit video cam sensor dialog definition ===
#================================================

import tkinter as tk
from tkinter import *
from tkinter import ttk
# --- Python 3.10 environment MAX is required
# --- 3.11 one is not supported yet
import carla

from Gui.BasicDialog import BasicDialog 
from Gui.ExtraScaleControl import ExtraScaleControlItem

# https://carla.readthedocs.io/en/0.9.15/tuto_first_steps/
class ChangeWeatherDlg(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Dialog result (True - save changes, otherwise False)
    result: False

    # --- Application settings object reference
    app_settings = None

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window reference
    # --- settings: application settings object reference
    def __init__(self, parent, settings):

        self.result = False

        self.app_settings = settings

        top = self.top = tk.Toplevel(parent)

        top.resizable(False, False)

        paramsFrame = Frame(top)
        paramsFrame.pack()

        scaleCloudiness = ExtraScaleControlItem(paramsFrame, "clouds", "cl", "CLOUDINESS",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.cloudiness, 1,
                                "  Clouds intensity (range 0 - 100)  ", False, True,
                                self.onParamChange)
        scaleCloudiness.grid(row=0, column=0, padx=5, pady=5, sticky="nwse")

        scaleRain = ExtraScaleControlItem(paramsFrame, "precip", "pr", "PRECIPITATION",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.precipitation, 1,
                                " Rain intensity (range 0 - 100) ", False, True,
                                self.onParamChange)
        scaleRain.grid(row=0, column=1, padx=5, pady=5, sticky="nwse")

        scalePuddles = ExtraScaleControlItem(paramsFrame, "puddle", "pd", "WATER ON ROAD",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.road_water, 1,
                                "Puddles intensity (range 0 - 100)", False, True,
                                self.onParamChange)
        scalePuddles.grid(row=0, column=2, padx=5, pady=5, sticky="nwse")

        scaleWind = ExtraScaleControlItem(paramsFrame, "wind", "wd", "WIND",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.wind_intensity, 1,
                                "Wind intensity (range 0 - 100)", False, True,
                                self.onParamChange)
        scaleWind.grid(row=0, column=3, padx=5, pady=5, sticky="nwse")

        scaleWetness = ExtraScaleControlItem(paramsFrame, "wetnes", "wt", "WETNESS (RGB ONLY)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.wetness, 1,
                                "Wetness intensity (range 0 - 100)", False, True,
                                self.onParamChange)
        scaleWetness.grid(row=0, column=4, padx=5, pady=5, sticky="nwse")

        scaleSunAzimuth = ExtraScaleControlItem(paramsFrame, "sunaz", "saz", "SUN AZIMUTH",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 360, settings.sun_azimuth_angle, 1,
                                "Sun azimuth angle (range 0 - 360)", False, True,
                                self.onParamChange)
        scaleSunAzimuth.grid(row=1, column=0, padx=5, pady=5, sticky="nwse")

        scaleSunAltitude = ExtraScaleControlItem(paramsFrame, "sunal", "sal", "SUN ALTITUDE",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', -90, 90, settings.sun_altitude_angle, 1,
                                "Sun altitude angle (range -90 - 90)", False, True,
                                self.onParamChange)
        scaleSunAltitude.grid(row=1, column=1, padx=5, pady=5, sticky="nwse")

        scaleFogConcentration = ExtraScaleControlItem(paramsFrame, "fogc", "fc", "FOG CONCENTRATION",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.fog_density, 1,
                                "Fog concentration (range 0 - 100)", False, True,
                                self.onParamChange)
        scaleFogConcentration.grid(row=1, column=2, padx=5, pady=5, sticky="nwse")

        scaleFogDistance = ExtraScaleControlItem(paramsFrame, "fogs", "fs", "FOG START DISTANCE",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 1000, settings.fog_distance, 1,
                                "Fog start distance (range 0 - 1000)", False, True,
                                self.onParamChange)
        scaleFogDistance.grid(row=1, column=3, padx=5, pady=5, sticky="nwse")

        scaleFogDensity = ExtraScaleControlItem(paramsFrame, "fogd", "fd", "FOG DENSITY",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 1000, settings.fog_falloff, 1,
                                "Fog density (range 0 - 1000)", False, True,
                                self.onParamChange)
        scaleFogDensity.grid(row=1, column=4, padx=5, pady=5, sticky="nwse")

        scaleScattering = ExtraScaleControlItem(paramsFrame, "sctr", "sct", "SCATTERING INTENCITY",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 1000, settings.scattering_intensity, 1,
                                "Light contribution to the fog (range 0-1000)", False, True,
                                self.onParamChange)
        scaleScattering.grid(row=2, column=0, padx=5, pady=5, sticky="nwse")

        scaleDustStorm = ExtraScaleControlItem(paramsFrame, "dsts", "dst", "DUST STORM",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, settings.dust_storm, 1,
                                "Dust storm intencity (range 0 - 100)", False, True,
                                self.onParamChange)
        scaleDustStorm.grid(row=2, column=1, padx=5, pady=5, sticky="nwse")

        # Actions buttons panel
        panelActions = Frame(top)
        panelActions.rowconfigure(0, weight=1)
        panelActions.columnconfigure(0)
        panelActions.columnconfigure(1)
        panelActions.pack(pady=5)

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=0, sticky="w", padx=10) 
        submitButton = ttk.Button(button_border, text=' Apply ', 
            style='W.TButton', command=self.apply)
        submitButton.pack(fill='both')

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=1, sticky="w", padx=10) 
        cancelButton = ttk.Button(button_border, text=' Cancel ', 
            style='W.TButton', command=self.cancel)
        cancelButton.pack(fill='both')

        self.center_window(top)

    # Apply changes button is clicked event handler
    def apply(self):
        self.result = True
        self.top.destroy()

    # Cancel changes button is clicked event handler
    def cancel(self):
        self.top.destroy()

    # --- Weather parameter is changed event handler
    # --- id: weather parameter identifier
    # --- val: weather parameter value
    def onParamChange(self, id, val):
        
        match id:

            case "cl":
                self.app_settings.cloudiness = val
            case "pr":
                self.app_settings.precipitation = val
            case "pd":
                self.app_settings.road_water = val
            case "wd":
                self.app_settings.wind_intensity = val
            case "wt":
                self.app_settings.wetness = val
            case "saz":
                self.app_settings.sun_azimuth_angle = val
            case "sal":
                self.app_settings.sun_altitude_angle = val
            case "fc":
                self.app_settings.fog_density = val
            case "fs":
                self.app_settings.fog_distance = val
            case "fd":
                self.app_settings.fog_falloff = val
            case "sct":
                self.app_settings.scattering_intensity = val
            case "dst":
                self.app_settings.dust_storm = val
