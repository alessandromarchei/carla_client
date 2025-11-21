
#====================================
# ===    CARLA emulator client    ===
# ===   -----------------------   ===
# ===  App main window definition ===
#====================================

import os
import time
import tkinter
import uuid
import threading
from Gui.TopDownView import TopDownViewDlg
import customtkinter
from pyclbr import Class
from tkinter import *
from ttkthemes import ThemedTk
from tkinter import messagebox
from turtle import bgcolor, left, width
from types import NoneType
from PIL import ImageTk, Image

from cv2 import NONE_POLISHER
from Gui import RightPane
from Gui.AddVehicle import AddVehicle
from Gui.ChangeWeather import ChangeWeatherDlg
from Gui.EditVideoCamDlg import EditVideoCamDlg
from Gui.ProgressWindow import ProgressWnd
from Gui.SetCollisions import SetCollisionsConditionsDlg
from Gui.SetObstacleParams import SetObstacleParamsDlg
from Gui.SpawnVehicle import SpawnVehicle
from Model.CollisionDef import CollisionDefinition
from Model.VideoCam import VideoCam
from tkinter import ttk

from Model.Vehicle import Vehicle
from Service.Enumerations import CarlaActor


def choose_vehicle(vehicles, name_contains):
    name_contains = name_contains.lower()
    for v in vehicles:
        if name_contains in v.Name.lower() or name_contains in v.Model.lower():
            return v
    return None



class MainWindow_headless(object):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Main window object
    rootWnd = None

    # Currently pressed key string
    pressedKey = None

    # Vehicles tree view
    gridVehicles = None

    # Sensors tree view
    gridSensors = None

    # All available vehicles collection
    availableVehicles = None

    # Used vehicles to be displayed collection
    usedVehicles = None

    # Currently selected vehicle
    selectedVehicle = None

    # Currently selected vehicle index
    selectedVehicleIndex = -1

    # Currently selected sensor
    selectedSensor = None

    # --- Application settings collection object
    app_settings = None

    # CARLA connection Url 
    urlCarla = None

    # CARLA connection port
    portCarla = None

    # Vehicle control unit connection Url
    urlVCU = None

    # Vehicle control unit connection port
    portVCU = None

    # CARLA traffic manager port
    portTMCarla = None

    # CARLA connection timeout
    timeoutCarla = None

    # CARLA simulator synchronuos mode flag
    useSyncMode = False

    # CARLA simulator desired FPS rate (-1 is variable)
    desiredFps = -1

    # --- Max allowed frames queue size before recreation
    maxFramesQueueSize = 50

    # --- Timeout for frames queue operations (sec)
    queueGetActionTimeout = 10

    # --- Use remote Carla server traffic manager flag
    useTrafficManager = True

    # --- Required count of generated traffic manager vehicles
    trafficManagerVehicles = 3

    # --- Required count of generated traffic manager pedestrians
    trafficManagerPedestrians = 3

    # Connect button object
    connectionButton = None

    # Vehicle control unit connection button
    controlUnitConnectionButton = None

    # Vehicle control unit connection status title
    controlUnitConnectionStatusTitle = None

    # Change weather button object
    changeWeatherButton = None

    # Change collision behaviour button object
    changeCollisionBehaviour = None

    # Current connection state
    connectionState = False

    # Connection status description 
    connectionStatusTitle = None

    # Control unit current connection state
    controlUnitConnectionState = False

    # Prediction unit current connection state
    predictionUnitConnectionState = False

    # Left panel object
    leftFrame = None

    # Right panel object
    rightFrame = None

    # Sensors panel title
    sensorsPanelTitle = None

    # Video stream receiver object
    videoStreamReceiver = None

    # CARLA world selection combo
    selectMapCombo = None

    # Current weather description text label
    weatherDesc = None

    #
    selectMapTitle = None

    #
    loadMapButton = None

    # Currently selected map complex name 
    selectedMap = None

    # --- CARLA server collaboration service object reference
    carlaConnectorService = None

    # --- Progress window object reference
    progressWindow = None

    # --- Spawn vehicle button
    installVehicle = None

    # --- Run selected vehicle on the road button
    runVehicle = None

    # --- Manually control selected vehicle on the road button
    controlVehicle = None

    # --- Generate obstacle for the selected vehicle button
    generateObstacle = None

    generationDescriptionText = None

    ctkbuttons = []

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- title: Main window title string
    # --- availableVehicles: Available vehicles collection (from CARLA)
    # --- carlaConnector: CARLA server collaboration service object reference
    # --- usedVehicles: Used vehicles collection(from Json files)
    # --- settings: application settings collection
    def __init__(self, title, carlaConnector, usedVehicles, settings):

        self.app_settings = settings

        # --- CARLA' connector service preparation. These callbacks act after buttons are pressed
        print("[headless gui] Callback bindings for CARLA service")
        self.carlaConnectorService = carlaConnector
        self.carlaConnectorService.onConnectionAttemptCompleted = self.onConnectionAttemptCompleted
        self.carlaConnectorService.onControlUnitConnectionAttemptCompleted = self.onControlUnitConnectionAttemptCompleted
        self.carlaConnectorService.onPredictionUnitConnectionAttemptCompleted = self.onPredictionUnitConnectionAttemptCompleted
        self.carlaConnectorService.onLoadWorldAttemptCompleted = self.onLoadWorldAttemptCompleted
        self.carlaConnectorService.onActorHasBeenSpawned = self.onActorHasBeenSpawned
        self.carlaConnectorService.onNewVideoFrameIsRecieved = self.onNewVideoFrameIsRecieved
        self.carlaConnectorService.onVehicleHasBeenStarted = self.onVehicleHasBeenStarted        
        self.carlaConnectorService.onMovingStep = self.onMovingStep

        self.usedVehicles = usedVehicles

        if len(usedVehicles) > 0:
            print(f"[headless gui] {len(usedVehicles)} used vehicles found") 
            print("[headless gui] Selecting first used vehicle as selected vehicle")
            self.selectedVehicle = usedVehicles[0]


        #gui dependencies removed
#         self.rootWnd = Tk();             # Initialize Tkinter framework

#         self.rootWnd.protocol("WM_DELETE_WINDOW", self.close_window)

#         self.rootWnd.title(title)        # Set window title

#  #       self.rootWnd.state('zoomed')     # Maximize window

#         self.rootWnd.rowconfigure(0, weight=16)

#         self.progressWindow = ProgressWnd(self.rootWnd)

#         # weight=0 to supress expanding!
#         self.rootWnd.columnconfigure(0, weight=1, uniform="column")
#         self.rootWnd.columnconfigure(1, weight=1, uniform="column")
        
#         # Left frame definition (vehicles and installed sensors)
#         self.leftFrame = Frame(self.rootWnd, background='lightsteelblue')

#         self.leftFrame.columnconfigure(0, weight=0)

#         connectionCommonFrame = Frame(self.leftFrame, name="$$$connectionframe$$$",
#                                       background='lightsteelblue')
#         connectionCommonFrame.pack(anchor="w", fill="x")

#         # Connection frame
#         urlTitle = Label(connectionCommonFrame, text="CARLA SERVER CONNECTION:", font=("Roboto", 11), 
#                          fg="white", bg="dodgerblue2")
#         urlTitle.pack(anchor="nw", fill="x", padx=1)
        
        print("[headless gui] Loading CARLA settings into variables")
        self.urlCarla = self.app_settings.carlaServerUrl
        self.portCarla = self.app_settings.carlaServerMainPort
        self.portTMCarla = self.app_settings.carlaServerTrafficManagerPort
        self.timeoutCarla = self.app_settings.carlaServerConnectionTimeout
        self.useSyncMode = self.app_settings.carlaServerGeneralMode
        self.desiredFps = self.app_settings.carlaServerRequiredFps
        self.maxFramesQueueSize = self.app_settings.maxFramesQueueSize
        self.queueGetActionTimeout = self.app_settings.queueGetActionTimeout
        self.useTrafficManager = self.app_settings.carlaServerUseTrafficManager
        self.trafficManagerVehicles = self.app_settings.carlaServerTrafficManagerRequiredVehicles
        self.trafficManagerPedestrians = self.app_settings.carlaServerTrafficManagerRequiredPedestrians
        self.urlVCU = self.app_settings.vehicleControlUnitAddress
        self.portVCU = self.app_settings.vehicleControlUnitPort
        self.urlPSU = self.app_settings.predictionUnitAddress
        self.portPSU_TX = self.app_settings.predictionUnit_TXPort
        self.portPSU_RX = self.app_settings.predictionUnit_RXPort

        #gui dependencies removed
        # urlFrame = Frame(connectionCommonFrame, background='lightsteelblue')
        # urlFrame.pack(pady=5)
        # urlFrame.rowconfigure(0, weight=1)
        # urlFrame.rowconfigure(1, weight=1)
        # urlFrame.columnconfigure(0, weight=0)
        # urlFrame.columnconfigure(1, weight=1)
        # urlFrame.columnconfigure(2, weight=0)
        # urlFrame.columnconfigure(3, weight=1)
        # urlFrame.columnconfigure(4, weight=0)
        # urlFrame.columnconfigure(5, weight=1)
        # urlFrame.columnconfigure(6, weight=0)
        # urlFrame.columnconfigure(7, weight=1)

        # urlSubTitle = Label(urlFrame, text="URL:", background='lightsteelblue', font=("Roboto", 10))
        # urlSubTitle.grid(row=0, column=0, padx=2)
        # urlEntry = customtkinter.CTkEntry(
        #     urlFrame, textvariable=self.urlCarla, corner_radius=5)
        # urlEntry.grid(row=0, column=1, sticky="nwse")

        # portTitle = Label(urlFrame, text="Port:", background='lightsteelblue', font=("Roboto", 10))
        # portTitle.grid(row=0, column=2, padx=2)
        # portEntry = customtkinter.CTkEntry(
        #     urlFrame, textvariable=self.portCarla, corner_radius=5)
        # portEntry.grid(row=0, column=3, sticky="nwse", padx=5)

        # portTMTitle = Label(urlFrame, text="TM port:", background='lightsteelblue', font=("Roboto", 10))
        # portTMTitle.grid(row=0, column=4, padx=2)
        # portTMEntry = customtkinter.CTkEntry(
        #     urlFrame, textvariable=self.portTMCarla, corner_radius=5)
        # portTMEntry.grid(row=0, column=5, sticky="nwse", padx=5)

        # timeoutTitle = Label(urlFrame, text="Timeout (sec):", background='lightsteelblue', font=("Roboto", 10))
        # timeoutTitle.grid(row=0, column=6, padx=2)
        # timeoutEntry = customtkinter.CTkEntry(
        #     urlFrame, textvariable=self.timeoutCarla, corner_radius=5)
        # timeoutEntry.grid(row=0, column=7, sticky="nwse", padx=5)
        
        # modeFrame = Frame(connectionCommonFrame, background='lightsteelblue')
        # modeFrame.pack(padx=5)
        # modeFrame.columnconfigure(0, weight=0)
        # modeFrame.columnconfigure(1)
        # modeFrame.columnconfigure(2, weight=10)

        # self.syncModeCheckbox = customtkinter.CTkCheckBox(modeFrame, 
        #     text = "Synchronous mode", 
        #     corner_radius=3, fg_color = ('green', 'white'),
        #     variable = self.useSyncMode, onvalue = 1, offvalue = 0) 
        # self.syncModeCheckbox.grid(row=0, column=0)
        # print(self.syncModeCheckbox)

        # timestampTitle = Label(modeFrame, text="Desired FPS (-1 means variable one):", background='lightsteelblue',
        #                        font=("Roboto", 10))
        # timestampTitle.grid(row=0, column=1, padx=5)
        # timestampEntry = customtkinter.CTkEntry(modeFrame, textvariable=self.desiredFps, corner_radius=5, width=100)
        # timestampEntry.grid(row=0, column=2, sticky="nwse")

        # --- Extra Carla server paremeters enter panel
        
        # extraServerParamsFrame = Frame(connectionCommonFrame, background='lightsteelblue')
        # extraServerParamsFrame.rowconfigure(0)
        # extraServerParamsFrame.rowconfigure(1, weight=10)
        # extraServerParamsFrame.rowconfigure(2)
        # extraServerParamsFrame.rowconfigure(3, weight=10)
        # extraServerParamsFrame.pack(pady=5)

        # maxQueueSizeTitle = Label(extraServerParamsFrame, text="Max frames queue size:", background='lightsteelblue',
        #                           font=("Roboto", 10))
        # maxQueueSizeTitle.grid(row=0, column=0)
        # maxQueueSizeEntry = customtkinter.CTkEntry(extraServerParamsFrame, textvariable=self.maxFramesQueueSize, corner_radius=5, width=100)
        # maxQueueSizeEntry.grid(row=0, column=1, sticky="nwse", padx=5)

        # getTimeoutTitle = Label(extraServerParamsFrame, text="Queue GET operation timeout (sec):", background='lightsteelblue', font=("Roboto", 10))
        # getTimeoutTitle.grid(row=0, column=2)
        # getTimeoutEntry = customtkinter.CTkEntry(extraServerParamsFrame, textvariable=self.queueGetActionTimeout, corner_radius=5, width=100)
        # getTimeoutEntry.grid(row=0, column=3, sticky="nwse", padx=5)

        # extraServerParamsFrame2 = Frame(connectionCommonFrame, background='lightsteelblue')
        # extraServerParamsFrame2.rowconfigure(0, weight=1)
        # extraServerParamsFrame2.columnconfigure(0)
        # extraServerParamsFrame2.columnconfigure(1)
        # extraServerParamsFrame2.columnconfigure(2, weight=20)
        # extraServerParamsFrame2.columnconfigure(3)
        # extraServerParamsFrame2.columnconfigure(4, weight=20)
        # extraServerParamsFrame2.columnconfigure(5)
        # extraServerParamsFrame2.pack()

        # self.syncModeCheckbox = customtkinter.CTkCheckBox(extraServerParamsFrame2, 
        #             text = "Generated traffic",
        #             variable = self.useTrafficManager, onvalue = 1, offvalue = 0, 
        #             corner_radius=3, fg_color = ('green', 'white'))

        # self.syncModeCheckbox.grid(row=0, column=0, padx=3)

        # vehiclesCountTitle = Label(extraServerParamsFrame2, text="Vehicles:", background='lightsteelblue', font=("Roboto", 10))
        # vehiclesCountTitle.grid(row=0, column=1)
        # vehiclesCountEntry = customtkinter.CTkEntry(extraServerParamsFrame2, width=150,
        #     textvariable=self.trafficManagerVehicles, corner_radius=5)
        # vehiclesCountEntry.grid(row=0, column=2, sticky="w", padx=5)

        # pedestriansCountTitle = Label(extraServerParamsFrame2, text="Pedestrians:", background='lightsteelblue', font=("Roboto", 10))
        # pedestriansCountTitle.grid(row=0, column=3)
        # pedestriansCountEntry = customtkinter.CTkEntry(extraServerParamsFrame2, textvariable=self.trafficManagerPedestrians, corner_radius=5)
        # pedestriansCountEntry.grid(row=0, column=4, sticky="w", padx=5)
        
        # button_border = Frame(extraServerParamsFrame2, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=5, sticky="w", padx=5)
        # self.changeCollisionButton = ttk.Button(button_border, text="Settings", 
        #     style='W.TButton', width=8, command=self.onChangeCollisions)
        # self.changeCollisionButton.pack(fill='both')
        print("[headless gui] Change collision button prepared")
        # self.onChangeCollisions()

        # #---------------------

        # controlUnitUrlFrame = Frame(connectionCommonFrame, background='lightsteelblue')
        # controlUnitUrlFrame.pack(pady=5)
        # controlUnitUrlFrame.rowconfigure(0, weight=1)
        # controlUnitUrlFrame.rowconfigure(1, weight=1)
        # controlUnitUrlFrame.columnconfigure(0)
        # controlUnitUrlFrame.columnconfigure(1)
        # controlUnitUrlFrame.columnconfigure(2)
        # controlUnitUrlFrame.columnconfigure(3, weight=10)
        # controlUnitUrlFrame.columnconfigure(4)
        # controlUnitUrlFrame.columnconfigure(5)
        # controlUnitUrlFrame.columnconfigure(6)
        # controlUnitUrlFrame.columnconfigure(7, weight=10)

        # controlUnitTitle = Label(controlUnitUrlFrame, text="Vehicle control unit (VSU):", background='lightsteelblue', font=("Roboto", 10, "bold"))
        # controlUnitTitle.grid(row=0, column=0, padx=5, columnspan=4, sticky="nw")

        # predictionTitle = Label(controlUnitUrlFrame, text="Traectory prediction unit (TPU):", background='lightsteelblue', font=("Roboto", 10, "bold"))
        # predictionTitle.grid(row=0, column=4, padx=5, columnspan=4, sticky="nw")

        # controlUnitUrlTitle = Label(controlUnitUrlFrame, text="Address:", background='lightsteelblue', font=("Roboto", 10))
        # controlUnitUrlTitle.grid(row=1, column=0, padx=5, sticky="w")
        # controlUnitUrlEntry = customtkinter.CTkEntry(controlUnitUrlFrame, textvariable=self.urlVCU, corner_radius=5)
        # controlUnitUrlEntry.grid(row=1, column=1, sticky="nwse")

        # controlUnitPortTitle = Label(controlUnitUrlFrame, text="Port:", background='lightsteelblue', font=("Roboto", 10))
        # controlUnitPortTitle.grid(row=1, column=2, padx=5)
        # controlUnitPortEntry = customtkinter.CTkEntry(controlUnitUrlFrame, textvariable=self.portVCU, corner_radius=5)
        # controlUnitPortEntry.grid(row=1, column=3, sticky="nw", padx=5)

        # predictionServerUrlTitle = Label(controlUnitUrlFrame, text="Address:", background='lightsteelblue', font=("Roboto", 10))
        # predictionServerUrlTitle.grid(row=1, column=4, padx=5, sticky="w")
        # predictionServerUrlEntry = customtkinter.CTkEntry(controlUnitUrlFrame, textvariable=self.urlPSU, corner_radius=5)
        # predictionServerUrlEntry.grid(row=1, column=5, sticky="nw")

        # predictionServerPortTitle = Label(controlUnitUrlFrame, text="Port:", background='lightsteelblue', font=("Roboto", 10))
        # predictionServerPortTitle.grid(row=1, column=6, padx=5)
        # predictionServerPortEntry = customtkinter.CTkEntry(controlUnitUrlFrame, textvariable=self.portPSU, corner_radius=5)
        # predictionServerPortEntry.grid(row=1, column=7, sticky="nwse", padx=5)

        # connectionFrame = Frame(connectionCommonFrame, background='lightsteelblue')
        # connectionFrame.pack(anchor="w", fill="x")
        # connectionFrame.columnconfigure(0, weight = 0)
        # connectionFrame.columnconfigure(1, weight = 0)
        # connectionFrame.columnconfigure(2, weight = 0)
        # connectionFrame.columnconfigure(3, weight = 1)

        # connectionFrame1 = Frame(connectionFrame, background='lightsteelblue')
        # connectionFrame1.grid(row=0)

        # button_border = Frame(connectionFrame1, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=1, sticky="w", pady=5, padx=10)
        # self.connectionButton =ttk.Button(button_border, text="Connect CARLA", 
        #     style='W.TButton', command=self.onConnectClick)
        # self.connectionButton.pack(fill='both')
        print("[headless gui] Connect CARLA button prepared")
        # self.onConnectClick()
        
        # self.imageCarlaStatusDisconnected = ImageTk.PhotoImage(Image.open("disconnected.png"))
        # self.imageCarlaStatusConnected = ImageTk.PhotoImage(Image.open("ok.png"))
        # self.imageCarlaStatus = Label(connectionFrame1, image = self.imageCarlaStatusDisconnected)
        # self.imageCarlaStatus.grid(row=0, column=0, sticky="w", pady=5, padx=5)

        # self.imageVCUDisconnected = ImageTk.PhotoImage(Image.open("disconnected.png"))
        # self.imageVCUConnected = ImageTk.PhotoImage(Image.open("ok.png"))
        # self.imageVCUStatus = Label(connectionFrame1, image = self.imageVCUDisconnected)
        # self.imageVCUStatus.grid(row=0, column=2, sticky="w", pady=5, padx=5)

        # self.imageTPUDisconnected = ImageTk.PhotoImage(Image.open("disconnected.png"))
        # self.imageTPUConnected = ImageTk.PhotoImage(Image.open("ok.png"))
        # self.imageTPUStatus = Label(connectionFrame1, image = self.imageTPUDisconnected)
        # self.imageTPUStatus.grid(row=0, column=4, sticky="w", pady=5, padx=5)

        # button_border = Frame(connectionFrame1, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=3, sticky="w", pady=5, padx=10)        
        # self.controlUnitConnectionButton = ttk.Button(button_border, text="Connect VCU", 
        #     style='W.TButton', command=self.onControlUnitConnectClick)
        # self.controlUnitConnectionButton.pack(fill='both')
        print("[headless gui] Connect VCU button prepared")
        # self.onControlUnitConnectClick()

        # button_border = Frame(connectionFrame1, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=5, sticky="w", pady=5, padx=10)        
        # self.predictionUnitConnectionButton = ttk.Button(button_border, text="Connect TPU", 
        #     style='W.TButton', command=self.onPredictionUnitConnectClick)
        # self.predictionUnitConnectionButton.pack(fill='both')
        print("[headless gui] Connect TPU button prepared")
        # self.onPredictionUnitConnectClick()

        # self.generationDescriptionText = Label(connectionFrame, text="Objects generation status is unknown yet", background='lightsteelblue', font=("Roboto", 10))
        # self.generationDescriptionText.grid(row=1, columnspan=2, sticky="w", padx=5)

        # self.prepareWeatherPanel(self.leftFrame)

        print("[headless gui] Loading CARLA world")
        # self.LoadCarlaWorld()

        # # Vehicles frame
        # vehiclesFrame = Frame(self.leftFrame, background='lightsteelblue')
        # vehiclesFrame.pack(expand=True, fill="both")
        # vehiclesTitle = Label(vehiclesFrame, text="VEHICLES LIST:", font=("Roboto", 11), 
        #                       fg="white", bg="dodgerblue2")
        # vehiclesTitle.pack(anchor="nw", padx=1, fill="x")

        # vehiclesGridFrame = Frame(vehiclesFrame)

        # self.gridVehicles = ttk.Treeview(vehiclesGridFrame,
        #     column=("Name", "Manufacturer", "Model", 
        #             "Class", "Type", "Status"), 
        #     height=3, show="headings")

        # vehiclesGridFrame.pack(anchor="nw", expand=True, fill="both")

        # scrollbar_yV = ttk.Scrollbar(vehiclesGridFrame, command=self.gridVehicles.yview)
        # scrollbar_xV = ttk.Scrollbar(vehiclesGridFrame, command=self.gridVehicles.xview, orient="horizontal")
        # self.gridVehicles.config(xscrollcommand=scrollbar_xV.set, yscrollcommand=scrollbar_yV.set)
        # scrollbar_yV.pack(fill="y", side="right")
        # scrollbar_xV.pack(fill="x", side="bottom")        
        # self.gridVehicles.pack(anchor="nw", expand=True, fill="both")

        print("[headless gui] Initializing vehicles list not implemented in headless mode")
        # self.initializeVehiclesList(self.usedVehicles, self.gridVehicles)

        # Vehicles actions panel
        # panelVehiclesActions = Frame(vehiclesFrame, background='lightsteelblue')
        # panelVehiclesActions.rowconfigure(0, weight=1)
        # panelVehiclesActions.rowconfigure(1, weight=1)
        # panelVehiclesActions.rowconfigure(1, weight=2)
        # panelVehiclesActions.columnconfigure(0)
        # panelVehiclesActions.pack(anchor="nw", padx=3)

        # ttk.Style().theme_use('clam')
        # style = ttk.Style()
        # style.configure('W.TButton', foreground = 'white', 
        #     relief='flat', background='dodgerblue2', font=("Roboto", 10))
        # style.map("W.TButton",
        #     foreground=[('pressed', 'white'), ('active', 'white'), ('disabled', 'slategray')],
        #     background=[('pressed', '!disabled', 'dodgerblue4'), ('active', 'dodgerblue3'), ('disabled', 'lightgray')])

        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=0, sticky="w", pady=10, padx=2)
        # selectVehicle = ttk.Button(button_border, text="Select", 
        #     style='W.TButton', width=7, command=self.onSelectVehicleClick)
        # selectVehicle.pack(fill='both')
        print("[headless gui] Select vehicle button not implemented in headless mode")
        # self.onSelectVehicleClick()

        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=1, sticky="w", pady=10, padx=2)
        # self.installVehicle = ttk.Button(button_border, text="Spawn", 
        #     style='W.TButton', width=8, command=self.onInstallVehicle)
        # self.installVehicle.pack(fill='both')
        print("[headless gui] Spawn vehicle button prepared")
        # self.onInstallVehicle()

        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=3, sticky="w", pady=10, padx=2)
        # removeVehicle = ttk.Button(button_border, text="Remove", 
        #     style='W.TButton', width=8, command=self.onRemoveVehicleClick)
        # removeVehicle.pack(fill='both')


        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=4, sticky="w", pady=10, padx=2)
        # self.runVehicle = ttk.Button(button_border, text="Auto-run", 
        #     style='W.TButton', width=8, command=self.onRunVehicleClick)
        # self.runVehicle.pack(fill='both')
        print("[headless gui] Auto-run vehicle button prepared")
        # self.onRunVehicleClick()

        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=5, sticky="w", pady=10, padx=2)
        # self.controlVehicle = ttk.Button(button_border, text=" Set as Ego ", 
        #     style='W.TButton', width=10, command=self.startControlVehicleClick)
        # self.controlVehicle.pack(fill='both')
        print("[headless gui] Set as Ego vehicle button prepared")
        # self.startControlVehicleClick()

        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=6, sticky="w", pady=10, padx=2)
        # self.generateObstacle = ttk.Button(button_border, text=" Set obstacle ", 
        #     style='W.TButton', width=12, command=self.setObstacleForVehicleClick)
        # self.generateObstacle.pack(fill='both')

        # button_border = Frame(panelVehiclesActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=7, sticky="w", pady=10, padx=2)
        # self.topDownView = ttk.Button(button_border, text="Bird-eye view", 
        #     style='W.TButton', width=12, command=self.showTopDownViewClick)
        # self.topDownView.pack(fill='both')

        # Installed sensors frame
        # sensorsFrame = Frame(self.leftFrame, background='lightsteelblue')
        # sensorsFrame.pack(expand=True, fill="both")

        # self.sensorsPanelTitle = Label(sensorsFrame, textvariable=self.sensorsPanelTitle, font=("Roboto", 11), 
        #                      fg="white", bg="dodgerblue2")
        # self.sensorsPanelTitle.pack(anchor="nw", padx=1, fill="x")

        # sensorsGridFrame = Frame(sensorsFrame)

        # self.gridSensors = ttk.Treeview(sensorsGridFrame,
        #     column=("colName", "colResolution", "colIsFront",
        #             "colPosition", "colYaw", "colFOV", "postProcessing"), 
        #     height=2, show="headings")

        # sensorsGridFrame.pack(anchor="nw", expand=True, fill="both")

        # scrollbar_yS = ttk.Scrollbar(sensorsGridFrame, command=self.gridVehicles.yview)
        # scrollbar_xS = ttk.Scrollbar(sensorsGridFrame, command=self.gridVehicles.xview, orient="horizontal")
        # self.gridSensors.config(xscrollcommand=scrollbar_xS.set, yscrollcommand=scrollbar_yS.set)
        # scrollbar_yS.pack(fill="y", side="right")
        # scrollbar_xS.pack(fill="x", side="bottom")        

        # self.gridSensors.pack(anchor="nw", expand=True, fill="both")

        # self.leftFrame.grid(row=0, column=0, sticky="nesw")

        print("[headless gui] Initializing sensors list in GUI")
        # self.initializeSensorsList(self.selectedVehicle, 
        #                            self.gridSensors)

        # Sensors actions panel
        # panelSensorsActions = Frame(sensorsFrame, height=1, background='lightsteelblue')
        # panelSensorsActions.rowconfigure(0)
        # panelSensorsActions.columnconfigure(0)
        # panelSensorsActions.columnconfigure(1)
        # panelSensorsActions.columnconfigure(2)
        # panelSensorsActions.pack(anchor="nw")

        # button_border = Frame(panelSensorsActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=0, sticky="w", pady=5, padx=5)
        # addSensor = ttk.Button(button_border, text="Add", 
        #     style='W.TButton', width=10, command=self.onAddSensorClick)
        # addSensor.pack(fill='both')
        print("[headless gui] Add sensor button prepared")
        # self.onAddSensorClick()

        # button_border = Frame(panelSensorsActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        # editSensor = ttk.Button(button_border, text="Edit", 
        #     style='W.TButton', width=10, command=self.onEditSensorClick)
        # editSensor.pack(fill='both')

        # button_border = Frame(panelSensorsActions, highlightbackground = "white", 
        #                  highlightthickness = 1, bd=0, background='white')        
        # button_border.grid(row=0, column=2, sticky="w", pady=5, padx=5)
        # removeSensor = ttk.Button(button_border, text="Remove", 
        #     style='W.TButton', width=10, command=self.onRemoveSensorClick)
        # removeSensor.pack(fill='both')

        # Right (actions) frame definition
        # self.rightFrame = RightPane.RightFrame(self.rootWnd, bgcolor="white", carlaServerConnector=self.carlaConnectorService)
        # self.rightFrame.grid(row=0, column=1, sticky="nesw")

        # self.enable_disable(self.rootWnd, "disabled")

        #self.rootWnd.bind_all("<Key>", self.onKeyPressed)


        # self.rootWnd.mainloop()          # Show window and process window messages

        self.run()
        #endless loop 
        # try:
        #     while True:
        #             time.sleep(0.1)
        # except KeyboardInterrupt:
        #     self.carlaConnectorService.StopThreads()
        #     print("[headless gui] Shutting down headless carla client.")

    #--------------------

    #---------------------------------------
    #--- Public methods (initialization) ---
    #---------------------------------------

    #--- Initialize sensors grid              ---
    #--- vehicle: Currently selected vehicle ---
    #--- gridSensors: Sensors grid control    ---
    # def initializeSensorsList(self, vehicle, gridSensors):
        
    #     for row in self.gridSensors.get_children():
    #         self.gridSensors.delete(row)
    #         self.rootWnd.update()
        
    #     self.selectedSensor = None

    #     gridSensors.column('# 0', minwidth=0, width=0, stretch=False)
    #     gridSensors.column("colName", anchor='center', stretch=True, minwidth=140)
    #     gridSensors.heading("colName", text="Name")
    #     gridSensors.column("colResolution", anchor='center', stretch=False, minwidth=80, width=80)
    #     gridSensors.heading("colResolution", text="Resolution")
    #     gridSensors.column("colIsFront", anchor='center', stretch=False, minwidth=170, width=50)
    #     gridSensors.heading("colIsFront", text="Front")
    #     gridSensors.column("colPosition", anchor='center', stretch=False, minwidth=170, width=130)
    #     gridSensors.heading("colPosition", text="Position (X/Y/Z)")
    #     gridSensors.column("colYaw", anchor='center', stretch=False, minwidth=170, width=60)
    #     gridSensors.heading("colYaw", text="Yaw")
    #     gridSensors.column("colFOV", anchor='center', minwidth=50, width=50, stretch=False)
    #     gridSensors.heading("colFOV", text="FOV (°)")
    #     gridSensors.column("postProcessing", anchor='center', minwidth=110, width=110, stretch=False)
    #     gridSensors.heading("postProcessing", text="Post processing")

    #     if vehicle is not None:
    #         for item in vehicle.InstalledVideoCams:
    #             if item is not None:
    #                 sensor: VideoCam = item
    #                 gridSensors.insert('', 'end',
    #                     values=(sensor.name,
    #                         "{0:.0f} * {1:.0f}".format(sensor.frameSizeX, sensor.frameSizeY),                  
    #                         "{}".format("Yes" if sensor.isFront else ""),
    #                         "{0:.2f} / {1:.2f} / {2:.2f}".format(
    #                             sensor.position.positionX, 
    #                             sensor.position.positionY, 
    #                             sensor.position.positionZ),
    #                         "{0:.2f}".format(sensor.rotationYaw),
    #                         "{0:.2f}".format(sensor.fieldOfVision),
    #                         "{}".format(sensor.postProcessing)))
    #         gridSensors.bind("<<TreeviewSelect>>", self.onSelectSensor)
    #         if len(gridSensors.get_children()) > 0:
    #             first = gridSensors.get_children()[0]
    #             gridSensors.focus(first)
    #             gridSensors.selection_set(first)
    #             self.selectedSensor = vehicle.InstalledVideoCams[0]

    def initializeSensorsList(self, vehicle, gridSensors):
        if gridSensors is None:
            # headless → just record selectedSensor correctly
            if vehicle is not None and len(vehicle.InstalledVideoCams) > 0:
                self.selectedSensor = vehicle.InstalledVideoCams[0]
            else:
                self.selectedSensor = None
            return

    #--- Initialize vehicles grid              ---
    #--- sensors: Provided vehicles collection ---
    #--- gridVehicles: Vehicles grid control    ---
    def initializeVehiclesList(self, vehicles, gridVehicles):

        style = ttk.Style(gridVehicles)
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="lightyellow2", foreground="black")
        style.map('Treeview', background=[('selected', 'palegreen1')])
        style.map('Treeview', foreground=[('selected', 'black')])

        gridVehicles.column('# 0', minwidth=0, width=0, stretch=False)
        gridVehicles.column("Name", anchor='center', stretch=True, width=100, minwidth=100)
        gridVehicles.heading("Name", text="Name")
        gridVehicles.column("Manufacturer", anchor='center', stretch=False, width=100, minwidth=100)
        gridVehicles.heading("Manufacturer", text="Manufacturer")
        gridVehicles.column("Model", anchor='center', stretch=False, minwidth=170, width=170)
        gridVehicles.heading("Model", text="Model")
        gridVehicles.column("Class", anchor='center', stretch=False, minwidth=80, width=80)
        gridVehicles.heading("Class", text="Class")
        gridVehicles.column("Type", anchor='center', minwidth=70, width=70, stretch=False)
        gridVehicles.heading("Type", text="Type")
        gridVehicles.column("Status", anchor='center', minwidth=90, width=90, stretch=False)
        gridVehicles.heading("Status", text="Status")
        
        gridVehicles.tag_configure('bold', font=('',8,'italic'), foreground="blue")
        gridVehicles.tag_configure('boldS', font=('',8,'bold'), foreground="darkred")

        if vehicles is not None:
            for item in vehicles:
                if item is not None:
                    vehicle: Vehicle = item
                    gridVehicles.insert('', 'end',
                        values=(vehicle.Name, vehicle.Manufacturer, vehicle.Model,
                                vehicle.Class, vehicle.BaseType, vehicle.get_status_text()))
            gridVehicles.unbind("<<TreeviewSelect>>")
            gridVehicles.bind("<<TreeviewSelect>>", self.onSelectVehicle)
            if len(gridVehicles.get_children()) > 0:
                first = gridVehicles.get_children()[0]
                gridVehicles.focus(first)
                gridVehicles.selection_set(first)

    #--------------------

    #------------------------------------------------
    #--- Public methods (control events handlers) ---
    #------------------------------------------------

    #--- Add sensor button is clicked event handler
    def onAddSensorClick(self):
        self.ProcessSensorButtonClick(True)

    #--- Edit sensor button is clicked event handler
    def onEditSensorClick(self):
        self.ProcessSensorButtonClick(False)

    # --- Change CARLA weather button is clicked
    def onChangeWeather(self):

        inputDialog = ChangeWeatherDlg(self.rootWnd, self.app_settings)
        
        self.rootWnd.wait_window(inputDialog.top)

        if inputDialog.result == True:

            self.weatherDesc.configure(text = self.app_settings.createWeatherDescription())

    # --- Change collisions conditions button is clicked event handler
    def onChangeCollisions(self):

        # inputDialog = SetCollisionsConditionsDlg(self.rootWnd, self.app_settings)
        
        # self.rootWnd.wait_window(inputDialog.top)

        # if inputDialog.result == True:
        #     print("OK")
        print("[headless gui] Change collisions conditions not implemented in headless mode")

    # --- Install vehicle to CARLA button is clicked
    def onInstallVehicle(self):

        if self.selectedVehicle.status == 0:
            if self.selectedVehicle is not None:
                inputDialog = SpawnVehicle(self.rootWnd, self.selectedVehicle)
            else:
                messagebox.showwarning(title="Warning", message="No selected vehicle")
                return
        
            self.rootWnd.wait_window(inputDialog.top)

            if inputDialog.result == True:

                # self.progressWindow.show("Spawning vehicle")

                # self.rightFrame.setSelectedVehicle(self.selectedVehicle)

                #self.rightFrame.focusOnTabVideo()

                activethread = self.carlaConnectorService.RunSpawnActorThread(self.selectedVehicle, CarlaActor.Vehicle, 
                    inputDialog.behaviorName.get(), self.progressWindow,
                    inputDialog.ignoreTrafficLights.get(),
                    inputDialog.ignoreStopSigns.get(),
                    inputDialog.ignoreVehicles.get())

                # self.progressWindow.wait(activethread)
        else:
            self.carlaConnectorService.UnspawnVehicle(self.selectedVehicle)
            self.selectedVehicle.status = 0
            self.processSpawnVehicle(self.selectedVehicle)

    #--- Remove vehicle button is clicked event handler
    def onRemoveVehicleClick(self):
        if self.selectedVehicle is None:
            messagebox.showwarning(title="Warning", message="No selected vehicle")
            return
        else:
            res = messagebox.askyesno("askyesno", "Remove selected vehicle?") 
            if(res == True):
                focused = self.gridVehicles.focus()
                self.gridVehicles.delete(focused)
                os.remove(".\{}.json".format(self.selectedVehicle.Uuid))
                if len(self.gridVehicles.get_children()) > 0:
                    first = self.gridVehicles.get_children()[0]
                    self.gridVehicles.focus(first)
                    self.gridVehicles.selection_set(first)
                    self.selectedVehicle = self.usedVehicles[0]

    # --- Run selected vehicle on the road button is clicked event handler
    def onRunVehicleClick(self):

        if self.selectedVehicle.status == 1:
            print("[headless gui] Starting vehicle auto-run")
            # self.progressWindow.show("Starting vehicle")
        
            activethread = self.carlaConnectorService.RunStartVehicleThread()

            # self.progressWindow.wait(activethread)
            self.selectedVehicle.status = 2

        else:

            self.carlaConnectorService.StopAutoRunning()

            self.selectedVehicle.status = 1
    
            self.processControlVehicleButton(self.selectedVehicle)

        self.processRunVehicleButton(self.selectedVehicle)

        row = self.gridVehicles.get_children()[self.selectedVehicleIndex]

        self.gridVehicles.set(row, column="Status", value=self.selectedVehicle.get_status_text())            

    # --- Start vehicle manual control button is clicked event handler 
    def startControlVehicleClick(self):

        text = ""
        status = ""
        val = 0

        row = self.gridVehicles.get_children()[self.selectedVehicleIndex]

        if self.selectedVehicle.status != 3:

            if self.selectedVehicle.status == 2:
                self.carlaConnectorService.StopAutoRunning()

            # self.rightFrame.HighlightControlledStreamWnd(self.selectedVehicle.Uuid, True)
            self.carlaConnectorService.SetSelectedVehicle(self.selectedVehicle.Uuid, True)
            val = 3
            self.gridVehicles.item(row, tags='boldS')
        else:
            
            self.selectedVehicle.status = 1
            self.gridVehicles.item(row, tags='bold')
            # self.rightFrame.HighlightControlledStreamWnd(self.selectedVehicle.Uuid, False)
            self.carlaConnectorService.SetSelectedVehicle(self.selectedVehicle.Uuid, False)
            self.carlaConnectorService.SetSelectedVehicle(None, True)
            val = 1

        self.runVehicle.configure(state=status)
        self.selectedVehicle.status = val
        self.processControlVehicleButton(self.selectedVehicle)
        self.processRunVehicleButton(self.selectedVehicle)
        self.gridVehicles.set(row, column="Status", value=self.selectedVehicle.get_status_text())            

    #--- Remove sensor button is clicked event handler
    def onRemoveSensorClick(self):
        if self.selectedSensor is None:
            print("[headless gui] No selected sensor to remove")
            # messagebox.showwarning(title="Warning", message="No selected sensor")
            return
        else:
            # res = messagebox.askyesno("askyesno", "Remove selected sensor?") 
            # if(res == True):
            #     focused = self.gridSensors.focus()
            #     self.gridSensors.delete(focused)
            #     self.selectedVehicle.InstalledVideoCams.remove(self.selectedSensor)
            #     self.selectedVehicle.serialize(".", True)
            print("[headless gui] Removing selected sensor")

    # --- Set obstacle before specified vehicle button click
    def setObstacleForVehicleClick(self):

        # inputDialog = SetObstacleParamsDlg(self.rootWnd)
        
        # self.rootWnd.wait_window(inputDialog.top)

        # if inputDialog.result == True:
        
        #     msg = self.carlaConnectorService.EmulateObstacle(self.selectedVehicleIndex, 
        #         inputDialog.obstacleKind.get(), 
        #         float(inputDialog.obstacleDistance.get()),
        #         float(inputDialog.obstacleAngle.get()),
        #         inputDialog.moveObstacle.get() == 1)

        #     if msg != "":
        #         messagebox.showwarning(title="Warning", message=msg)
        print("[headless gui] Set obstacle for vehicle not implemented in headless mode")

    #--- Connect button is clicked event handler
    def onConnectClick(self):

        # self.controlUnitConnectionButton.configure(state='normal')
        self.s = True

        if self.connectionState == False:

            # --- REAL CONNECT TO CARLA
            self.ConnectToCarlaServer()

        else:
            # self.connectionButton.configure(text="Connect CARLA")
            self.connectionState = False;
            # self.imageCarlaStatus.configure(image=self.imageCarlaStatusDisconnected)
            # self.enable_disable(self.rootWnd, "disabled")
            # --- Stop video stream receiver thread
            if self.videoStreamReceiver is not None:
                self.videoStreamReceiver.Stop()

    #--- Connect button is clicked event handler
    def onControlUnitConnectClick(self):

        if self.controlUnitConnectionState == False:

            self.saveSettings()
            self.carlaConnectorService.ConnectVCU(self.urlVCU, self.portVCU)

        else:
            self.carlaConnectorService.DisconnectVCU()
            self.controlUnitConnectionButton.configure(text="Connect VCU")
            self.controlUnitConnectionState = False;
            # self.imageVCUStatus.configure(image=self.imageVCUConnected)


    #--- Connect button is clicked event handler
    def onPredictionUnitConnectClick(self):

        if self.predictionUnitConnectionState == False:

            self.saveSettings()
            print("CONNECT TPU button pressed")
            self.carlaConnectorService.ConnectTPU()

        else:
            self.carlaConnectorService.DisconnectTPU()
            self.predictionUnitConnectionButton.configure(text="Connect TPU")
            self.predictionUnitConnectionState = False;
            # self.imageTPUStatus.configure(image=self.imageTPUDisconnected)

    #--- Process (add/edit) sensor 
    #--- addNew: add new sensor if true, otherwise edit existing one
    def ProcessSensorButtonClick(self, addNew):
        
        inputDialog = None
        prevName = None

        if addNew == True:
            inputDialog = EditVideoCamDlg(self.rootWnd)
        else:
            if self.selectedSensor is None:
                messagebox.showwarning(title="Warning", message="No selected sensor")
                return
            else:
                prevName = self.selectedSensor.name
                inputDialog = EditVideoCamDlg(self.rootWnd, self.selectedSensor)
        
        self.rootWnd.wait_window(inputDialog.top)

        if inputDialog.result == True:
            
            if(addNew == True):

                self.gridSensors.insert('', 'end',
                    values=(inputDialog.sensor.name,
                        "{0:.0f} * {1:.0f}".format(inputDialog.sensor.frameSizeX, inputDialog.sensor.frameSizeY),                  
                        "{}".format("Yes" if inputDialog.sensor.isFront else ""),
                        "{0:.2f} / {1:.2f} / {2:.2f}".format(
                            inputDialog.sensor.position.positionX, 
                            inputDialog.sensor.position.positionY, 
                            inputDialog.sensor.position.positionZ),
                        "{0:.2f}".format(inputDialog.sensor.rotationYaw),
                        "{0:.2f}".format(inputDialog.sensor.fieldOfVision),
                        "{}".format(inputDialog.sensor.postProcessing)))
                inputDialog.sensor.Uuid = str(uuid.uuid4())
                self.selectedVehicle.InstalledVideoCams.append(inputDialog.sensor)
                self.selectedVehicle.serialize(".", True)
            else:
                focused = self.gridSensors.focus()

                self.gridSensors.item(focused,
                    values=(inputDialog.sensor.name,
                        "{0:.0f} * {1:.0f}".format(inputDialog.sensor.frameSizeX, inputDialog.sensor.frameSizeY),                  
                        "{}".format("Yes" if inputDialog.sensor.isFront else ""),
                        "{0:.2f} / {1:.2f} / {2:.2f}".format(
                            inputDialog.sensor.position.positionX, 
                            inputDialog.sensor.position.positionY, 
                            inputDialog.sensor.position.positionZ),
                        "{0:.2f}".format(inputDialog.sensor.rotationYaw),
                        "{0:.2f}".format(inputDialog.sensor.fieldOfVision),
                        "{}".format(inputDialog.sensor.postProcessing)))

                self.selectedVehicle.serialize(".", True)

    # --- Connect to remote CARLA server attempt   
    def ConnectToCarlaServer(self):

        # self.progressWindow.show("Connecting to CARLA server")

        self.saveSettings()

        activethread = self.carlaConnectorService.RunCarlaConnectionThread(self.app_settings)

        # self.progressWindow.wait(activethread)
        
        print("[headless gui] CONNECTED TO CARLA SERVER")

    # --- Load CARLA world (city map)
    def LoadCarlaWorld(self):

        # --- Split selected map complex name to extract city one
        # items = self.selectedMap.get().split("/")

        # self.progressWindow.show("Loading world map")

        #check if really needed
        # thread = self.carlaConnectorService.RunLoadCarlaWorldThread(self.app_settings, "")
        # thread.join()

        print("[headless gui] CARLA world loaded completed")

    #--------------------

    #----------------------------------------
    #--- Public methods (events handlers) ---
    #----------------------------------------

    # --- Connection to CARLA server attempt is completed event handler
    # --- result: connection attempt result
    # --- maps: CARLA' available maps collection
    # --- error: connection error description (if any)
    def onConnectionAttemptCompleted(self, result, maps, error):

        # if result == True:
        #     self.connectionButton.configure(text="Disconnect CARLA")
        #     self.connectionState = True;
        #     self.imageCarlaStatus.configure(image=self.imageCarlaStatusConnected)
        #     self.FillMapsCombo(maps)
        #     self.selectMapTitle.configure(state="normal")
        #     self.selectMapCombo.configure(state="normal")
        #     self.loadMapButton.configure(state="normal")
        #     self.changeWeatherButton.configure(state="normal")
        #     self.changeWeatherButton.configure(state="normal")
        #     self.weatherDesc.configure(state="normal")

        # else:
        #     messagebox.showerror(title="Error", message=error)

        # self.progressWindow.hide()

        if result:
            print("[headless_gui] CARLA connected")
            self.maps = maps
            self.connectionState = True;
        else:
            print("[headless_gui][ERROR] CARLA connection error")

    
    # --- Connection to VCU attempt is completed event handler
    # --- result: connected successfully if true, otherwise false
    def onControlUnitConnectionAttemptCompleted(self, result):

        # if result == True:
        #     self.controlUnitConnectionButton.configure(text="Disconnect VCU")
        #     self.controlUnitConnectionState = True;
        #     self.imageVCUStatus.configure(image=self.imageVCUStatusConnected)
        # else:
        #     messagebox.showwarning(title="Warning", message="Error connection to vehicle control unit")
        if result:
            print("[headless_gui] VCU connected")
            self.controlUnitConnectionState = True;
        else:
            print("[headless_gui][ERROR] VCU connection error")


    # --- Connection to VCU attempt is completed event handler
    # --- result: connected successfully if true, otherwise false
    def onPredictionUnitConnectionAttemptCompleted(self, result):

        # if result == True:
        #     self.predictionUnitConnectionButton.configure(text="Disconnect TPU")
        #     self.predictionUnitConnectionState = True;
        #     self.imageTPUStatus.configure(image=self.imageTPUConnected)
        # else:
        #     messagebox.showwarning(title="Warning", message="Error connection to vehicle control unit")
        if result:
            print("[headless_gui] TPU connected")
            self.predictionUnitConnectionState = True;
        else:
            print("[headless_gui][ERROR] TPU connection error")


    # --- Load CARLA' world (city map) attempt is completed event handler
    # --- result: connection attempt result
    # --- vehicles: CARLA' vehicles collection
    # --- error: connection error description (if any)
    # --- description: traffic generation results description
    def onLoadWorldAttemptCompleted(self, result, vehicles, error, description):

        if result == True:
            
            print("[headless_gui] CARLA world loaded with {} vehicles".format(len(vehicles)))
            # --- Create displayable own vehicles list
            self.availableVehicles = list()
        
            for vehicle in vehicles:

                svar = ""

                if len(vehicle.tags) > 2:
                    svar = vehicle.tags[2]

                ownVehicle = Vehicle(str(uuid.uuid4()), "", vehicle.tags[1],
                                 svar, "", 
                                 str(vehicle.get_attribute("generation")), 
                                 vehicle.id, 
                                 vehicle.get_attribute("base_type").as_str(),
                                 vehicle.get_attribute("special_type").as_str(),
                                 vehicle.get_attribute("has_lights").as_bool(),
                                 vehicle.get_attribute("has_dynamic_doors").as_bool())

                self.availableVehicles.append(ownVehicle)
            
            print("[headless_gui] Available vehicles list created with {} vehicles".format(len(self.availableVehicles)))
            # self.processControlVehicleButton(self.selectedVehicle)
            # self.processRunVehicleButton(self.selectedVehicle)
        else:
            messagebox.showerror(title="Error", message=error)


    # --- Load CARLA' world (city map) attempt is completed event handler
    # --- result: connection attempt result
    # --- vehicles: CARLA' vehicles collection
    # --- error: connection error description (if any)
    def onActorHasBeenSpawned(self, result, vehicle, error):

        # self.progressWindow.hide()

        if result == False:
            # messagebox.showerror(title="Error", message=error)
            print("[headless_gui][ERROR] Vehicle spawning error: {}".format(error))
        else:
            self.selectedVehicle.status = 1
            # self.installVehicle.configure(state="disabled")
            # self.generateObstacle.configure(state="normal")
            # self.processRunVehicleButton(self.selectedVehicle)
            # row = self.gridVehicles.get_children()[self.selectedVehicleIndex]
            
            # self.gridVehicles.set(row, column="Status", value=self.selectedVehicle.get_status_text())            

            # self.processControlVehicleButton(self.selectedVehicle)
            # self.processSpawnVehicle(self.selectedVehicle)
            
            # self.gridVehicles.item(row, tags='bold')
            self.carlaConnectorService.SetSelectedVehicle(self.selectedVehicle.Uuid, False)
            # self.rightFrame.AddSpawnedVehicle(self.selectedVehicle)

    # --- New video frame is recieved event handler
    # --- frame: newly recieved video frame byte array
    # --- params: parent sensor parameters
    def onNewVideoFrameIsRecieved(self, sensorNum, frame, raw_data, params,
                                clientFps, averageFps, serverFps):

        # GUI mode?
        if getattr(self, "rightFrame", None) is not None:
            try:
                self.rightFrame.NewVideoFrameReceived(
                    sensorNum, frame, raw_data, params,
                    clientFps, averageFps, serverFps
                )
            except Exception as e:
                print("[ERROR] GUI callback failed:", e)
        else:
            # CLI mode—ignore or print once
            # print(f"[CLI] Frame for sensor {sensorNum} (no GUI)")
            pass


    # --- Vehicle has been started on auto-pilot event handler
    # --- result: event result (True/False)
    # --- error: event error (if any)
    def onVehicleHasBeenStarted(self, result, error):

        self.progressWindow.hide()

        self.processRunVehicleButton(self.selectedVehicle)
        self.processControlVehicleButton(self.selectedVehicle)

        if result == False:
            messagebox.showerror(title="Error", message=error)

    # --- CARLA' world tick is done event handler
    # --- params: current moving parameters object
    def onMovingStep(self, params):

        self.rightFrame.onMovingStep(params)
        print("--------------- SENSOR (MAIN WND): {}".format(params.sensorIndex))

    #--------------------

    #---------------------------------
    #--- Public methods (services) ---
    #---------------------------------

    # --- Fill available maps combobox by read maps
    # --- maps: CARLA' available maps collection
    def FillMapsCombo(self, maps):

        if maps is not None:
            self.selectedMap.set(maps[1])
            self.selectMapCombo.configure(values = maps)  

    # --- Create map (world) selection panel
    # --- parent: parent frame
    def prepareMapSelectionPanel(self, parent):

        mapSelectionPanel = Frame(parent, background='lightsteelblue')
        mapSelectionPanel.pack(padx=5, pady=5, fill="x")

        mapSelectionPanel.rowconfigure(0, weight=1)
        mapSelectionPanel.columnconfigure(0)
        mapSelectionPanel.columnconfigure(1, weight=2)
        mapSelectionPanel.columnconfigure(2)

        self.selectMapTitle = Label(mapSelectionPanel, text="Select map to be used:", 
                                    background='lightsteelblue', font=("Roboto", 10))
        self.selectMapTitle.grid(row=0, column=0, sticky="nwse")

        self.selectedMap = StringVar()

        self.selectMapCombo = customtkinter.CTkComboBox(mapSelectionPanel, state="readonly",
            values=[], variable=self.selectedMap, width=400)
        self.selectMapCombo.update()

        self.selectMapCombo.grid(row=0, column=1, padx=5)

        button_border = Frame(mapSelectionPanel, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=2)
        self.loadMapButton = ttk.Button(button_border, text="  Load  ", 
            style='W.TButton', command=self.LoadCarlaWorld)
        self.loadMapButton.pack(fill='both')

    # --- Enable or disable children controls tree
    # --- frame: parent control
    # --- status: required status (normal or disabled)
    def enable_disable(self, frame, status, numcall = 1):

        for child in frame.winfo_children():

            print(child.widgetName)

            if child.widgetName == 'canvas':
                return

            if child._name == "wheels":
                child = child.viewPort     
                
            if child._name != "$$$connectionframe$$$":
                try:
                    if child.widgetName != 'frame':  # frame has no state, so skip
                        child.configure(state=status)
                    else:
                        self.enable_disable(child, status, 0)
                        if child._name == "motionparamstab":
                            if status == "normal":
                                child.event_generate("<<PanelStatusChanged>>")

                except Exception as e:
                    self.enable_disable(child, status, 0)

    #--------------------

    #-------------------------------------------
    #--- Public methods (process selections) ---
    #-------------------------------------------

    #--- Vehicles treeview selection is changed event handler
    #--- param: event parameters (widget member is used)
    def onSelectVehicle(self, param):
        
        listView = param.widget
        
        self.selectedVehicleIndex = listView.index(listView.selection())

        self.selectedVehicle = self.usedVehicles[self.selectedVehicleIndex]
        
        print("SELECTED VEHICLE STATUS: {}".format(self.selectedVehicle.status))

        if self.connectionState == True:
            self.generateObstacle.configure(state="normal")

            print("SELECTED STATUS: {}".format(self.selectedVehicle.status))

            if self.selectedVehicle.status > 0:
                self.installVehicle.configure(state="disabled")
            else:
                self.installVehicle.configure(state="normal")
                self.runVehicle.configure(state="disabled")
                self.generateObstacle.configure(state="disabled")

        self.initializeSensorsList(self.selectedVehicle, 
                                   self.gridSensors)

        self.processSpawnVehicle(self.selectedVehicle)        
        self.processControlVehicleButton(self.selectedVehicle)
        self.processRunVehicleButton(self.selectedVehicle)

        self.rightFrame.setSelectedVehicle(self.selectedVehicle)
        self.sensorsPanelTitle.configure(text="{} ({} / {}) INSTALLED SENSORS"
                                 .format(self.selectedVehicle.Name,
                                         self.selectedVehicle.Manufacturer,
                                         self.selectedVehicle.Model))
        
        if self.selectedVehicle.status > 0:
            self.carlaConnectorService.SetSelectedVehicle(self.selectedVehicle.Uuid, False)

    #--- Sensors treeview selection is changed event handler
    #--- param: event parameters (widget member is used)
    def onSelectSensor(self, param):
        
        listView = param.widget
        selectedIndex = listView.index(listView.selection())

        if len(self.selectedVehicle.InstalledVideoCams) > 0:

            self.selectedSensor = self.selectedVehicle.InstalledVideoCams[selectedIndex]

            if self.videoStreamReceiver is not None:
                self.videoStreamReceiver.switchVideo("USM")
        
    #--- Select vehicle to the set 
    def onSelectVehicleClick(self):

        inputDialog = AddVehicle(self.rootWnd, 
                                 self.availableVehicles)
        
        # self.rootWnd.wait_window(inputDialog.top)

        if inputDialog.result == True:
            self.gridVehicles.insert('', 'end',
                values=(inputDialog.selectedVehicleObj.Name,
                    inputDialog.selectedVehicleObj.Manufacturer, 
                    inputDialog.selectedVehicleObj.Model,
                    inputDialog.selectedVehicleObj.Class, 
                    inputDialog.selectedVehicleObj.BaseType, 
                    inputDialog.selectedVehicleObj.SpecialType))

            inputDialog.selectedVehicleObj.Uuid = str(uuid.uuid4())
            self.usedVehicles.append(inputDialog.selectedVehicleObj)
            self.selectedVehicle = inputDialog.selectedVehicleObj
            self.selectedVehicle.serialize(".", True)
            first = self.gridVehicles.get_children()[-1]
            self.gridVehicles.focus(first)
            self.gridVehicles.selection_set(first)

    # --- Main window close is requested event handler
    def close_window(self):
        
        try:
            print( "Window closed")
            if self.carlaConnectorService.vcu_Connector is not None:
                self.carlaConnectorService.vcu_Connector.stopRequested = True
            self.carlaConnectorService.StopThreads()
            self.rootWnd.destroy()
        except:
            pass

        self.saveSettings()

    # --- Save application settings to Json file
    def saveSettings(self):

        self.app_settings.carlaServerUrl = self.urlCarla
        self.app_settings.carlaServerMainPort = self.portCarla
        self.app_settings.carlaServerTrafficManagerPort = self.portTMCarla
        self.app_settings.carlaServerConnectionTimeout = self.timeoutCarla
        self.app_settings.carlaServerGeneralMode = self.useSyncMode
        self.app_settings.carlaServerRequiredFps = self.desiredFps

        self.app_settings.maxFramesQueueSize = self.maxFramesQueueSize
        self.app_settings.queueGetActionTimeout = self.queueGetActionTimeout

        self.app_settings.carlaServerUseTrafficManager = self.useTrafficManager
        self.app_settings.carlaServerTrafficManagerRequiredVehicles = self.trafficManagerVehicles
        self.app_settings.carlaServerTrafficManagerRequiredPedestrians = self.trafficManagerPedestrians

        self.app_settings.vehicleControlUnitAddress = self.urlVCU
        self.app_settings.vehicleControlUnitPort = self.portVCU

        self.app_settings.predictionUnitAddress = self.urlPSU
        self.app_settings.predictionUnit_TXPort = self.portPSU_TX
        self.app_settings.predictionUnit_RXPort = self.portPSU_RX

        self.app_settings.serialize(True)
  
    #--------------------

    # --- Weather related functions -------

    # --- 
    def prepareWeatherPanel(self, parent):

        weatherPanel = Frame(parent, background='lightsteelblue')
        weatherPanel.columnconfigure(0, weight=1)
        weatherPanel.columnconfigure(1)
        weatherPanel.pack(padx=5, pady=5, fill="x")
        self.weatherDesc = Label(weatherPanel, 
                            wraplength=500, text=self.app_settings.createWeatherDescription(),
                            background='lightsteelblue', font=("Roboto", 10))
        self.weatherDesc.grid(row=0, column=0)

        button_border = Frame(weatherPanel, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=1)        
        self.changeWeatherButton = ttk.Button(button_border, text="Set weather", 
            style='W.TButton', width=14, command=self.onChangeWeather)
        self.changeWeatherButton.pack(fill='both')

    # -------------------------------------

    # --- Process current vehicle selection
    # vehicle: currently selected vehicle
    def processSpawnVehicle(self, vehicle):
        if vehicle is not None:
            if self.connectionState == True:
                match vehicle.status:
                    case 0:
                        self.installVehicle.configure(text='Spawn')
                    case 1:
                        self.installVehicle.configure(text='Unspawn')
                    case 2:
                        self.installVehicle.configure(state='disabled')
                    case 3:
                        self.installVehicle.configure(state='disabled')
            else:
                self.installVehicle.configure(state='disabled')
        else:
            self.installVehicle.configure(state='disabled')

    # --- Process the status of "Control vehicle" button
    # vehicle: currently selected vehicle
    def processControlVehicleButton(self, vehicle):

        if vehicle is not None:
            if self.connectionState == True:
                match vehicle.status:
                    case 0:
                        self.installVehicle.configure(state='normal')
                        self.carlaConnectorService.stopTopDownSensor()
                        # self.topDownView.configure(state='disabled')
                        self.controlVehicle.configure(state='disabled')
                        self.controlVehicle.configure(text='Set as Ego')
                    case 1:
                        self.installVehicle.configure(state='normal')
                        self.carlaConnectorService.stopTopDownSensor()
                        # self.topDownView.configure(state='disabled')
                        self.controlVehicle.configure(text='Set as Ego')
                        if self.carlaConnectorService.selected_controlled_vehicle is not None:
                            self.controlVehicle.configure(state='disabled')
                        else:         
                            self.controlVehicle.configure(state='normal')
                    case 2:
                        self.installVehicle.configure(state='disabled')
                        self.controlVehicle.configure(text='Set as Ego')
                        self.controlVehicle.configure(state='disabled')
                        self.carlaConnectorService.stopTopDownSensor()
                        # self.topDownView.configure(state='disabled')
                    case 3:
                        self.installVehicle.configure(state='disabled')
                        self.controlVehicle.configure(state='normal')
                        self.controlVehicle.configure(text='Stop Ego')
                        # self.topDownView.configure(state='normal')
            else:
                self.controlVehicle.configure(state='disabled')
                self.controlVehicle.configure(text='Set as Ego')
                self.carlaConnectorService.stopTopDownSensor()
                # self.topDownView.configure(state='disabled')
        else:
            self.controlVehicle.configure(state='disabled')
            self.controlVehicle.configure(text='Set as Ego')
            self.carlaConnectorService.stopTopDownSensor()
            # self.topDownView.configure(state='disabled')

    # --- Process the status of "Auto-run vehicle" button
    # vehicle: currently selected vehicle
    def processRunVehicleButton(self, vehicle):

        if vehicle is not None:
            if self.connectionState == True:
                match vehicle.status:
                    case 0:
                        self.runVehicle.configure(state='disabled')
                        self.runVehicle.configure(text='Auto-run')
                    case 1:
                        self.runVehicle.configure(state='normal')
                        self.runVehicle.configure(text='Auto-run')
                        self.controlVehicle.configure(text='Set as Ego')
                        if self.carlaConnectorService.selected_controlled_vehicle is not None:
                            self.controlVehicle.configure(state='disabled')
                        else:         
                            self.controlVehicle.configure(state='normal')
                    case 2:
                        self.runVehicle.configure(text='Stop')
                        self.runVehicle.configure(state='enabled')
                    case 3:
                        self.runVehicle.configure(state='disabled')
                        self.runVehicle.configure(text='Auto-run')
            else:
                self.runVehicle.configure(state='disabled')
        else:
            self.runVehicle.configure(state='disabled')

    # --- Show top-down view window button is clicked event handler
    def showTopDownViewClick(self):
        
        print("Show top-down view button is pressed")
        print("[headless_gui] Top-down view is not available in headless mode")

        # if self.carlaConnectorService.topDownSensor is None:
        #     self.carlaConnectorService.startTopDownSensor()
        #     topDownViewWnd = TopDownViewDlg(self.rootWnd, 
        #                          self.carlaConnectorService)
        #     self.rootWnd.wait_window(topDownViewWnd.top)
        # else:
        #     self.carlaConnectorService.stopTopDownSensor()


# ------------------------------------------------------
    # Commands
    # ------------------------------------------------------

    def cmd_ConnectToCarlaServer(self):

        if self.connectionState == False:
            self.saveSettings()
            
            print(f"[CLI] Connecting to CARLA at {self.urlCarla}:{self.portCarla}...")
            self.carlaclient_thread = self.carlaConnectorService.RunCarlaConnectionThread(self.app_settings)
            self.carlaclient_thread.join()
            print("[CLI] Connected.")
        else:
            print("[CLI] Already connected.")

    def cmd_DisconnectFromCarlaServer(self):

        if self.connectionState == True:
            self.saveSettings()
            
            print(f"[CLI] Disconnecting from CARLA at {self.urlCarla}:{self.portCarla}...")
            self.carlaclient_thread.stop()
            self.carlaclient_thread.join()
            print("[CLI] Disconnected.")

            self.connectionState = False
        else:
            print("[CLI] Already disconnected.")

    def cmd_LoadCarlaWorld(self, map_name):
        if self.connectionState == False:
            print("[CLI] Not connected. Run 'connect' first.")
            return

        # 1) Get available maps directly from CARLA
        try:
            available_maps = self.carlaConnectorService.carlaClient.get_available_maps()
        except Exception as e:
            print("[CLI] ERROR: Unable to query available maps:", e)
            return

        # Normalize
        # Example incoming -> "/Game/Carla/Maps/Town10HD_Opt"
        normalized_maps = [os.path.basename(m) for m in available_maps]

        print("\n[CLI] Available maps:")
        for m in normalized_maps:
            print("  -", m)
        print()

        # 2) Check if user map_name exists
        if map_name not in normalized_maps:
            print(f"[CLI] ERROR: Map '{map_name}' is NOT available.")
            print("Choose one from the list above.")
            return

        print(f"[CLI] Loading world '{map_name}' ...")

        # 3) Prepare the internal name EXACTLY like GUI does:
        #    (GUI uses: self.selectedMap.get().split('/'), take last item)
        selected_map_full = None
        for m in available_maps:
            if m.endswith(map_name):
                selected_map_full = m
                break

        if selected_map_full is None:
            print(f"[CLI] ERROR: Could not find full CARLA path for map '{map_name}'.")
            return

        # 4) extract short name (same logic used in GUI)
        items = selected_map_full.split("/")
        short_name = items[-1]

        # 5) Load the world using the CARLA connector thread
        activethread = self.carlaConnectorService.RunLoadCarlaWorldThread(
            self.app_settings,
            short_name
        )

        activethread.join()
        print("[CLI] World loaded successfully.\n")


        #now here laod the vehicles available in the world
        print("[CLI] Loading available vehicles in the world...")


    def cmd_ListAvailableMaps(self):
        if self.connectionState == False:
            print("[CLI] Not connected. Run 'connect' first.")
            return

        # 1) Get available maps directly from CARLA
        try:
            available_maps = self.carlaConnectorService.carlaClient.get_available_maps()
        except Exception as e:
            print("[CLI] ERROR: Unable to query available maps:", e)
            return

        # Normalize
        # Example incoming -> "/Game/Carla/Maps/Town10HD_Opt"
        normalized_maps = [os.path.basename(m) for m in available_maps]

        print("\n[CLI] Available maps:")
        for m in normalized_maps:
            print("  -", m)
        print()

    def cmd_Cars(self):
        if not self.connectionState:
            print("[CLI] Not connected. Run 'connect' first.")
            return

        if self.availableVehicles is not None and len(self.availableVehicles) > 0:
            print("\n[CLI] AVAILABLE VEHICLES:")
            for v in self.availableVehicles:
                print(f"  - {v.Name} ({v.Manufacturer} {v.Model})   (blueprint={v.BlueprintID})")

        print("\n[CLI] CURRENT USED VEHICLES:")
        for v in self.usedVehicles:
            print(f"  - {v.Name}  (status={v.status})")
        print()

    def cmd_ShowSelectedCar(self):
        if self.selectedVehicle is None:
            print("[CLI] No vehicle selected.")
            return

        v = self.selectedVehicle
        print("\n[CLI] SELECTED VEHICLE:")
        print(f"  Name: {v.Name}")
        print(f"  Manufacturer: {v.Manufacturer}")
        print(f"  Model: {v.Model}")
        print(f"  UUID: {v.Uuid}")
        print(f"  Status: {v.status}")
        print("")

    def cmd_ShowSensorsSelectedCar(self):
        if self.selectedVehicle is None:
            print("[CLI] No vehicle selected.")
            return

        v = self.selectedVehicle

        print(f"\n[CLI] SENSORS for {v.Name}:")
        if len(v.InstalledVideoCams) == 0:
            print("  No sensors installed.")
            return

        for cam in v.InstalledVideoCams:
            print("  ---------------- VIDEO CAMERA ----------------")
            print(f"    Name:            {cam.name}")
            print(f"    Resolution:      {cam.frameSizeX:.0f} × {cam.frameSizeY:.0f}")
            print(f"    Front Camera:    {'Yes' if cam.isFront else 'No'}")
            print(f"    Position:        X={cam.position.positionX:.2f}, "
                f"Y={cam.position.positionY:.2f}, Z={cam.position.positionZ:.2f}")
            print(f"    Yaw:             {cam.rotationYaw:.2f}°")
            print(f"    Field of View:   {cam.fieldOfVision:.2f}°")
            print(f"    Post-Processing: {cam.postProcessing}")
            print("  -----------------------------------------------\n")


    """
    Equivalent to OnSelectVehicle in GUI
    It selects a vehicle from usedVehicles by name and makes it selectedVehicle
    """
    def cmd_SelectCar(self, name):
        
        if len(self.usedVehicles) == 0:
            print("[CLI] No used vehicles loaded.")
            return

        # Find matching vehicle by name (case insensitive)
        idx = -1
        for i, v in enumerate(self.usedVehicles):
            if v.Name.lower() == name.lower():
                idx = i
                break

        if idx == -1:
            print(f"[CLI] Vehicle '{name}' not found in usedVehicles.")
            return

        # ==== REPLICATE GUI LOGIC =====
        self.selectedVehicleIndex = idx
        self.selectedVehicle = self.usedVehicles[idx]
        v = self.selectedVehicle

        print(f"[CLI] SELECTED VEHICLE: {v.Name}")
        print(f"[CLI] Status = {v.status}")

        if self.connectionState:
            print("[CLI] Connected: evaluating status...")

            if v.status > 0:
                print("[CLI] Vehicle already spawned or running. Spawn disabled.")
            else:
                print("[CLI] Vehicle not spawned yet. Spawn enabled.")

        # These calls configure internal
        # self.processSpawnVehicle(v)   uses gui
        # self.processControlVehicleButton(v)
        # self.processRunVehicleButton(v)

        # simulate setSelectedVehicle
        self.carlaConnectorService.SetSelectedVehicle(v.Uuid, False)

        # Sensors update (no GUI, but internal logic preserved)
        self.initializeSensorsList(v, None)   

        print(f"[CLI] Vehicle '{v.Name}' selected.")

    """
    Equivalent to OnSelectVehicleClick in GUI
    Bring a vehicle from availableVehicles to usedVehicles
    """
    def cmd_AddCar(self, name):
        # Find in available vehicles
        match = None
        for v in self.availableVehicles:
            if v.Name.lower() == name.lower():
                match = v
                break

        if match is None:
            print(f"[CLI] ERROR: Vehicle '{name}' not found in availableVehicles.")
            return

        # duplicate object (as GUI does)
        import copy
        new_vehicle = copy.deepcopy(match)
        new_vehicle.Uuid = str(uuid.uuid4())
        new_vehicle.status = 0

        # append
        self.usedVehicles.append(new_vehicle)
        self.selectedVehicle = new_vehicle
        self.selectedVehicleIndex = len(self.usedVehicles) - 1

        # serialize like GUI
        new_vehicle.serialize(".", True)

        print(f"[CLI] Added vehicle '{new_vehicle.Name}'.")

    """
    Equivalent to OnRemoveVehicleClick in GUI
    """
    def cmd_RemoveCar(self, name):
        idx = -1
        for i, v in enumerate(self.usedVehicles):
            if v.Name.lower() == name.lower():
                idx = i
                break

        if idx == -1:
            print(f"[CLI] Vehicle '{name}' not found.")
            return

        v = self.usedVehicles[idx]

        # remove JSON file as GUI does
        json_path = f"./{v.Uuid}.json"
        if os.path.exists(json_path):
            os.remove(json_path)

        del self.usedVehicles[idx]

        # reselect similar to GUI
        if len(self.usedVehicles) > 0:
            self.selectedVehicle = self.usedVehicles[0]
            self.selectedVehicleIndex = 0
        else:
            self.selectedVehicle = None
            self.selectedVehicleIndex = -1

        print(f"[CLI] Vehicle '{name}' removed.")

    """
    Emulates the OnInstallVehicle in GUI
    """
    def cmd_spawn(self, veh_name=None, behavior="NORMAL"):

        # -----------------------------------
        # CASE 1 — spawn selected vehicle
        # -----------------------------------
        if veh_name is None:
            if self.selectedVehicle is None:
                print("[CLI] ERROR: No vehicle selected. Use 'select_car <name>' or specify a name: spawn <name>")
                return
        else:
            # -----------------------------------
            # CASE 2 — spawn vehicle by name
            # -----------------------------------
            self.selectedVehicle = choose_vehicle(self.usedVehicles, veh_name)
            if self.selectedVehicle is None:
                print(f"[CLI] ERROR: Vehicle '{veh_name}' not found in USED vehicles.")
                print("Use 'cars' to list available used vehicles.")
                return
            # update current selection

        print(f"[CLI] Spawning vehicle: {self.selectedVehicle.Name} with behavior {behavior}")

        if self.selectedVehicle.status == 0:
            ignoreTrafficLights = False
            ignoreStopSigns = False
            ignoreVehicles = False
        # Spawn using internal CARLA service (same as GUI)
            activethread = self.carlaConnectorService.RunSpawnActorThread(self.selectedVehicle, CarlaActor.Vehicle, 
                behavior, None,
                ignoreTrafficLights,
                ignoreStopSigns,
                ignoreVehicles)
            
            activethread.join()

        print("[CLI] Vehicle spawned successfully.")

    def cmd_ConnectTPU(self):
        self.onPredictionUnitConnectClick()


    def cmd_autorun(self):
        if self.spawned_vehicle is None:
            print("[CLI] Spawn a vehicle first.")
            return
        print("[CLI] Starting autorun...")
        th = self.service.RunStartVehicleThread()
        th.join()
        print("[CLI] Autorun started.")

    def cmd_stop(self):
        print("[CLI] Stopping autorun...")
        self.service.StopAutoRunning()
        print("[CLI] Stopped.")

    def cmd_quit(self):
        print("[CLI] Exiting...")
        self.service.StopThreads()
        exit(0)

    # ------------------------------------------------------
    # Interactive loop
    # ------------------------------------------------------

    def run(self):
        print("==========================================")
        print("     CARLA HEADLESS INTERACTIVE CLI")
        print("==========================================")
        print("Commands:")
        print("   connect")
        print("   disconnect")
        print("   load <map_name>")
        print("   maps")
        print("   cars")
        print("   show_selected_car")
        print("   show_sensors_selected_car")
        print("   select_car <vehicle_name>")
        print("   add_car <vehicle_name> WIP")
        print("   remove_car <vehicle_name> WIP")
        print("   spawn <vehicle_name> [behavior]")
        print("   connect_tpu")
        print("   autorun")
        print("   stop")
        print("   quit")
        print("==========================================")


        print("[CLI] Automatically connecting to CARLA server...")
        self.cmd_ConnectToCarlaServer()
        self.cmd_LoadCarlaWorld("Town10HD_Opt")
        self.cmd_SelectCar("MINI CAR")

        while True:
            try:
                cmd = input("> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == "connect":
                    self.cmd_ConnectToCarlaServer()

                elif cmd[0] == "disconnect":
                    self.cmd_DisconnectFromCarlaServer()

                elif cmd[0] == "load":
                    ##retrieve second cli argument as map name
                    if len(cmd) < 2:
                        print("Usage: load <map_name>")
                        print("Using default map: Town10HD_Opt")
                        self.map = "Town10HD_Opt"
                    else:
                        self.map = cmd[1]

                    self.cmd_LoadCarlaWorld(self.map)
                
                elif cmd[0] == "maps":
                    self.cmd_ListAvailableMaps()

                elif cmd[0] == "cars":
                    self.cmd_Cars()

                elif cmd[0] == "show_selected_car":
                    self.cmd_ShowSelectedCar()

                elif cmd[0] == "show_sensors_selected_car":
                    self.cmd_ShowSensorsSelectedCar()
                
                elif cmd[0] == "select_car":
                    if len(cmd) < 2:
                        print("Usage: select_car <vehicle_name>")
                    else:
                        self.cmd_SelectCar(" ".join(cmd[1:]))

                elif cmd[0] == "add_car":
                    if len(cmd) < 2:
                        print("Usage: add_car <vehicle_name>")
                        continue
                    self.cmd_AddCar(cmd[1])

                elif cmd[0] == "remove_car":
                    if len(cmd) < 2:
                        print("Usage: remove_car <vehicle_name>")
                        continue
                    self.cmd_RemoveCar(cmd[1])

                elif cmd[0] == "spawn":
                    if len(cmd) == 1:
                        self.cmd_spawn()
                    elif len(cmd) == 2:
                        self.cmd_spawn(cmd[1])
                    elif len(cmd) >= 3:
                        self.cmd_spawn(cmd[1], cmd[2])

                elif cmd[0] == "connect_tpu":
                    self.cmd_ConnectTPU()

                elif cmd[0] == "autorun":
                    self.cmd_autorun()

                elif cmd[0] == "stop":
                    self.cmd_stop()

                elif cmd[0] == "quit":
                    self.cmd_quit()

                else:
                    print("Unknown command:", cmd[0])

            except KeyboardInterrupt:
                print("\n[CLI] Ctrl+C received, shutting down.")
                self.cmd_quit()
    
    def LoadAvailableCars(self, vehicles, description):

        # --- Create displayable own vehicles list
        self.availableVehicles = list()
    
        for vehicle in vehicles:

            svar = ""

            if len(vehicle.tags) > 2:
                svar = vehicle.tags[2]

            ownVehicle = Vehicle(str(uuid.uuid4()), "", vehicle.tags[1],
                                svar, "", 
                                str(vehicle.get_attribute("generation")), 
                                vehicle.id, 
                                vehicle.get_attribute("base_type").as_str(),
                                vehicle.get_attribute("special_type").as_str(),
                                vehicle.get_attribute("has_lights").as_bool(),
                                vehicle.get_attribute("has_dynamic_doors").as_bool())

            self.availableVehicles.append(ownVehicle)
