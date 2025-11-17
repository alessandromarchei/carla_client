
#==============================================
# ===         CARLA emulator client         ===
# ===   ---------------------------------   ===
# ===  Main window' right panel definition  ===
#==============================================

from http import client
from tkinter import *
from tkinter import ttk
import customtkinter
from PIL import ImageTk, Image

from Gui.VideoStreamTab import VideoStreamTabItem
from Gui.WheelsParamsTab import WheelsParamsTabItem

# --- TRAFFIC GENERATION
# --- Remaining moving parameters
# --- https://github.com/carla-simulator/carla/blob/dev/PythonAPI/examples/sensor_synchronization.py

# DONE --- TO DO - no focus after spawning
# DONE --- TO DO - move extra motion params to video tab
# DONE --- TO DO - remove motion params tab
# DONE --- TO DO - apply control to controlled vehicle only
# DONE --- TO DO - add "Release" button to motion params

class RightFrame(Frame):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Page main tab control
    tabControl = None

    # Panel title
    labelTitle = None

    # --- Video stream tab item
    tabVideo = None

    # --- Currently selected vehicle
    selectedVehicle = None

    # --- Carla service connector object reference
    carlaServerConnector: None

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window object
    # --- bgcolor: panel background color
    # --- carlaServerConnector: Carla server connector object reference
    def __init__(self, parent, bgcolor, carlaServerConnector):
        
        self.carlaServerConnector = carlaServerConnector

        self.carlaServerConnector.OnVehicleControlMessageReceived = self.OnVehicleControlMessageReceived

        super().__init__(parent, bg=bgcolor,
                         highlightbackground="black", highlightthickness=1)

        self.labelTitle = Label(self, text="SPAWNED VEHICLES VIDEO SENSORS STREAMS:", 
                                fg="white", bg="dodgerblue2", font=("Roboto", 11))
        self.labelTitle.pack(anchor="w", padx=1, pady=1, fill="x")

        #self.tabControl = ttk.Notebook(self)
        #self.tabControl.bind("<KeyPress>", self.onKeyPressed)

        #tabWheels = WheelsParamsTabItem(self.tabControl, "white")

        self.tabVideo = VideoStreamTabItem(self, "white", carlaServerConnector)
        #self.tabVideo.bind("<KeyPress>", self.onKeyPressed)

        #self.tabControl.add(self.tabVideo, text='VIDEO STREAM')
        #self.tabControl.add(tabWheels, text='WHEELS')

        #self.tabControl.pack(expand=True, fill="both")
        self.tabVideo.pack(expand=True, fill="both")

    #-----------------------
    #--- Public methods  ---
    #-----------------------

    # --- Set panel title
    # --- vehicle: currently selected vehicle
    def setSelectedVehicle(self, vehicle):
        self.selectedVehicle = vehicle
        #self.tabMotionParams.setActiveVehicle(vehicle)
        #title = "SELECTED VEHICLE: {} ({} / {})".format(
        #            self.selectedVehicle.Name,
        #            self.selectedVehicle.Manufacturer,
        #            self.selectedVehicle.Model)

        #self.labelTitle.configure(text=title)

    # --- New video frame is received event handler
    # --- frame: newly recieved video frame byte array
    # --- params: parent sensor parameters
    def NewVideoFrameReceived(self, sensorNum, frame, raw_data, params,
                              clientFps, averageFps, serverFps):
        
        self.tabVideo.NewVideoFrameReceived(sensorNum, frame, raw_data, params,
                                            clientFps, averageFps, serverFps)
            
    # --- Vechicle control unit message is received event handler
    # --- dataPackage: receieved data package
    def OnVehicleControlMessageReceived(self, rawData, dataPackage):
        self.tabVideo.UpdateVCUValues(rawData)
        self.tabVideo.scaleSteering.setValue(dataPackage.wheelAngle)
        self.tabVideo.scaleThrottling.setValue(dataPackage.acceleratorPosition)
        self.tabVideo.scaleBraking.setValue(dataPackage.brakePosition)

    # --- Add spawned vehicle to the video frames tab
    # --- uuid: controlled vehicle object
    def AddSpawnedVehicle(self, vehicle):
        self.tabVideo.AddSpawnedVehicle(vehicle)

    # --- Highlight currently controlled video stream parent frame
    # --- uuid: Currently controlled video stream parent frame vehicle Id
    # --- select: select new controlled vehicle if True, remove selection if False
    def HighlightControlledStreamWnd(self, uuid, select):

        print("Controlled vehicle index: {}".format(uuid))             
        self.tabVideo.HighlightControlledStreamWnd(uuid, select)

    # --- CARLA' world tick is done event handler
    # --- params: current moving parameters object
    def onMovingStep(self, params):

        self.tabVideo.onMovingStep(params)
