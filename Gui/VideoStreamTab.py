
#==================================================
# ===          CARLA emulator client            ===
# ===   ------------------------------------    ===
# ===  Video stream panel tab panel definition  ===
#==================================================

# --- https://www.youtube.com/watch?v=yufUiCDfB10
# --- https://www.youtube.com/watch?v=7oUqRIysbag

from io import BytesIO
from pydoc import text
from time import time
from tkinter import *
from tkinter.tix import Control
from PIL import ImageTk, Image
from tkinter import ttk
import math
import customtkinter
from multiprocessing import Process, Queue
import numpy as np
import time
import cv2
import os
from Gui.VideoSensorThread import VideoSensorThreadItem
from Gui.ExtraScaleControl import ExtraScaleControlItem

# https://github.com/carla-simulator/data-collector/issues/18
# https://stackoverflow.com/questions/70275298/how-to-display-rgb-data-as-image-in-tkinter
# https://blog.wuhanstudio.uk/blog/carla-tutorial-basic/

class VideoStreamTabItem(Frame):

    #-----------------
    #--- Constants ---
    #-----------------

    # --- Maximum video stream windows rows
    maxRows = 2

    # --- Maximum video stream windows columns
    maxColumns = 3

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # --- Video streams parent frames collection
    videoStreamsFrames = []

    # --- Video streams parent internal frames collection
    videoStreamsInternalFrames = []

    # --- Video streams windows collection
    videoStreamsWindows = []

    # --- Video stream windows array
    videoStreamsLabels = []

    # --- Video stream titles array
    videoStreamsTitles = []

    # --- Video stream subtitles array
    videoStreamsSubTitles = []

    # --- Current server and client FPS labels array
    labelsFps = []

    # --- Resized image frame objects array (TO AVOID FLICKERING)
    resizedSavedImages = []

    # --- Currently selected video thumbnail window index
    selectedStreamIndexes = []

    # --- Full size video streams threads
    threads = []

    # --- Spawned sensors collection
    activeSensors = []

    # --- Currently displayed vehicles collection
    vehicles = []

    # --- Currently controlled vehicle video stream window index
    currently_controlled_vehicle_sensors = []

    # --- Currently shown sensors collection
    shown_sensors = []

    # --- Carla server connector object reference
    carlaServerConnector = None

    # --- Steering scale control
    scaleSteering = None;

    # --- Throttling scale control
    scaleThrottling = None;

    # --- Braking scale control
    scaleBraking = None;

    # --- 
    vehicleAppended = -1

    # --- Currently active manual gear
    activeGear = 1

    # --- Currently selected manual gear name
    mgVar = None    

    # --- Moving parameters text (first row)
    labelsMovingParams1 = []

    # --- Moving parameters text (second row)
    labelsMovingParams2 = []

    # --- Moving parameters text (third row)
    labelsMovingParams3 = []

    # --- Moving parameters text (fourth row)
    labelsMovingParams4 = []

    # --- Requested background color
    bgcolor: None

    # --- Currently processed by prediction unit image frame
    labelProcessedImagesStream: None

    # --- 
    processedImage: None

    # --- 
    savedProcessedImage: None

    # --- store last prediction for each mode (1=segmentation, 2=depth,...)
    lastPredictionsByMode = {}      # mode → numpy image (BGR)
    lastTkImagesByMode = {}         # mode → ImageTk.PhotoImage reference
    displayOrder = []               # ordered list of modes to display


    # --- Full size processed image show in OpenCV window thread
    processedImageCVThread = None

    isKeyboardControlShown = False

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window object
    # --- bgcolor: panel background color
    # --- carlaServerConnector: Carla server connector object reference
    def __init__(self, parent, bgcolor, carlaServerConnector):
        
        super().__init__(parent, bg=bgcolor,
                          highlightbackground="black", highlightthickness=1)

        self.rowconfigure(0, weight=4)
        self.rowconfigure(2, weight=3)
        self.columnconfigure(0, weight=1)

        self.frameSpawnedSensors = Frame(self)
        self.frameSpawnedSensors.grid(row=0, sticky="nwse")

        self.frameProcessedSensors = Frame(self)
        self.frameProcessedSensors.grid(row=1)

        self.bgcolor = bgcolor

        self.carlaServerConnector = carlaServerConnector

        self.carlaServerConnector.onPredictionUnitReplyReceived = self.onPredictionUnitReplyReceived

        # --- Grid for video sensors thumbnails

        for i in range(self.maxRows):
            self.frameSpawnedSensors.rowconfigure(i, weight=2, uniform="row")

        for j in range(self.maxColumns):
            self.frameSpawnedSensors.columnconfigure(j, weight=1, uniform="column")

        sensorIndex = 1

        for i in range(self.maxRows):
            for j in range(self.maxColumns):

                frame = Frame(self.frameSpawnedSensors, highlightbackground="black", highlightthickness=1, background='skyblue4')
                frame.grid(row=i, column=j, sticky="nwse")

                internalFrame = Frame(frame, background='skyblue4')
                internalFrame.pack()
                internalFrame.rowconfigure(0, weight = 1)
                #internalFrame.place(relx=.5, rely=.7, anchor="c")

                labelVideoStreamViewer = Label(internalFrame, image=None, background='skyblue4', font=("Roboto", 10))
                labelVideoStreamViewer.bind("<Button-1>", lambda event, i = sensorIndex - 1: self.showStreamInOpenCV(i))                
                labelVideoStreamViewer.grid(row=0)#.pack()pack(pady=0, anchor="n")

                labelTitle = Label(internalFrame, text="Sensor #{}".format(sensorIndex),
                                   font=("Roboto", 7), bd=-2, background='skyblue4', foreground='white',
                                   activeforeground='white', disabledforeground='white')
                labelTitle.grid(row=1)#.pack()

                labelSubTitle = Label(internalFrame, font=("Roboto", 7), bd=-2, background='skyblue4',
                                      foreground='white')
                labelSubTitle.grid(row=3)#.pack()

                labelFps = Label(internalFrame, text="", font=("Roboto", 7), bd=-2, background='skyblue4',
                                 foreground='white')
                labelFps.grid(row=3)#.pack()

                labelMovingParams1 = Label(internalFrame, text="",
                                           font=("Roboto", 7), bd=-2, background='skyblue4',
                                           foreground='white')
                self.labelsMovingParams1.append(labelMovingParams1)
                labelMovingParams1.grid(row=4)#.pack()

                labelMovingParams2 = Label(internalFrame, text="",
                                           font=("Roboto", 7), bd=-2, background='skyblue4',
                                           foreground='white')
                self.labelsMovingParams2.append(labelMovingParams2)
                labelMovingParams2.grid(row=5)#.pack()
               
                labelMovingParams3 = Label(internalFrame, text="",
                                           font=("Roboto", 7), bd=-2, background='skyblue4',
                                           foreground='white')
                self.labelsMovingParams3.append(labelMovingParams3)
                labelMovingParams3.grid(row=6)#.pack()

                labelMovingParams4 = Label(internalFrame, text="",
                                           font=("Roboto", 7), bd=-2, background='skyblue4',
                                           foreground='white')
                self.labelsMovingParams4.append(labelMovingParams4)
                labelMovingParams4.grid(row=7)#.pack()

                self.videoStreamsFrames.append(frame)
                self.videoStreamsInternalFrames.append(internalFrame)
                self.videoStreamsWindows.append(labelVideoStreamViewer)
                self.videoStreamsLabels.append(None)
                self.resizedSavedImages.append(None)
                self.videoStreamsTitles.append(labelTitle)
                self.videoStreamsSubTitles.append(labelSubTitle)
                self.labelsFps.append(labelFps)

                self.threads.append(None)

                self.activeSensors.append(False)

                sensorIndex = sensorIndex + 1

        self.preparePredictionImageFrame()

        self.steeringTitle = StringVar()
        self.throttlingTitle = StringVar()
        self.brakingTitle = StringVar()

        self.onSteeringChange("", 0);
        self.onThrottlingChange("", 0);
        self.onBrakingChange("", 0);

        self.steering = DoubleVar()
        self.throttling = DoubleVar()
        self.braking = DoubleVar()
        
        style = ttk.Style()
        style.configure("inactive.Horizontal.TScale", background="black",
                        troughcolor='gray77', troughrelief="sunken")

        self.styleSelected = ttk.Style()
        self.styleSelected.configure("active.Horizontal.TScale", background="black",
                        troughcolor='limegreen', troughrelief="sunken")

        self.controlFrame = Frame(self, highlightbackground="black", highlightthickness=1)

        self.manualGearStatus = IntVar() 
        self.handBrakeStatus = IntVar() 
        self.reverseMovingStatus = IntVar() 

        self.extraParamsFrame = Frame(self, background='lightsteelblue', name="extraparamsframe",
                         highlightbackground="black", highlightthickness=1)

        #self.prepareMainParamsPanel(bgcolor)
        #self.prepareExtraParamsPanel(bgcolor)

        #self.vcuDataFrame = Frame(self, background='lightsteelblue', name="extraparamsframe",
        #                 highlightbackground="black", highlightthickness=1)

        #self.vcuDataFrame.grid(sticky="nwse", columnspan=self.maxColumns)
        #self.vcuDataLabel = Label(self.vcuDataFrame, text="VCU data:", bg='lightsteelblue', font=("Roboto", 10))
        #self.vcuDataLabel.pack(padx=5, pady=3, fill="x")

    #-----------------------
    #--- Public methods  ---
    #-----------------------

    # --- New video frame is received event handler
    # --- sensorNum: sensor ordinal number
    # --- frame: newly recieved video frame byte array
    # --- raw_data: raw image data to be shown in OpenCV window
    # --- params: parent sensor parameters
    def NewVideoFrameReceived(self, sensorNum, frame, raw_data, params,
                              clientFps, averageFps, serverFps):

        if frame is not None:

            try:

                if self.activeSensors[sensorNum] == True:
                    self.threads[sensorNum].current_frame = raw_data

                w = int(self.winfo_width() / self.maxColumns) - 20
                h = int(self.winfo_height() / self.maxRows) - self.videoStreamsTitles[sensorNum].winfo_height() - self.videoStreamsSubTitles[sensorNum].winfo_height()

                resizedImage = self.ResizeImage(frame, w, h, params.imageRatio)

                if resizedImage is not None:

                    self.videoStreamsLabels[sensorNum] = ImageTk.PhotoImage(image=resizedImage)

                    self.videoStreamsWindows[sensorNum].config(
                        image=self.videoStreamsLabels[sensorNum])

                    self.videoStreamsTitles[sensorNum].config(
                            text=params.parentVehicleName)

                    self.videoStreamsSubTitles[sensorNum].config(
                            text=params.sensorName)

                    self.labelsFps[sensorNum].configure(
                            text="Server FPS: {} / Client FPS: {}".format(int(serverFps), int(clientFps)))

                    # --- To avoid flickering
                    self.resizedSavedImages[sensorNum] = self.videoStreamsLabels[sensorNum]

            except Exception as e:
                print("Error drawing: ".format(e))

            if self.vehicleAppended == sensorNum:
                self.carlaServerConnector.hideProgressWindow()
                self.vehicleAppended = -1
        
    # --- Display full-sized selected stream in OpenCV window
    # --- index: currebtly selected video stream index
    def showStreamInOpenCV(self, index):

        self.processedImagesFrame.focus_set()

        if index != -1:
            self.selectedStreamIndex = index

            self.threads[index] = VideoSensorThreadItem("Video stream", index + 1, 
                self.IsSensorOnCurrentlyControlledVehicle(index),
                self.shown_sensors[index].frameSizeX,
                self.shown_sensors[index].frameSizeY) 

            self.threads[index].onThreadStopped = self.onThreadStopped

            self.threads[index].start()

            self.activeSensors[index] = True
        else:
            self.processedImageCVThread = VideoSensorThreadItem("PROCESSED IMAGE", -1, 
                False, 640, 320)
            self.processedImageCVThread.start()
            self.processedImageCVThread.onThreadStopped = self.onProcessedImageCVThreadStopped

    # --- Full-size video stream window is closed event handler
    def onThreadStopped(self, sensorIndex):

        self.activeSensors[sensorIndex - 1] = False

    # --- Highlight currently controlled video stream parent frame
    # --- uuid: Currently controlled video stream parent frame vehicle Id
    # --- select: select new controlled vehicle if True, remove selection if False
    def HighlightControlledStreamWnd(self, uuid, select):

        if select == True:
            i = 0
            for v in self.vehicles:
                if v.Uuid == uuid:

                    color = "palegreen"

                    if self.shown_sensors[i].isFront == True:
                        color = "yellow2"

                    self.videoStreamsFrames[i].configure(background=color)
                    self.videoStreamsInternalFrames[i].configure(background=color)
                    self.videoStreamsTitles[i].configure(background=color, foreground='black')
                    self.videoStreamsSubTitles[i].configure(background=color, foreground='black')
                    self.labelsFps[i].configure(background=color, foreground='black')
                    self.labelsMovingParams1[i].configure(background=color, foreground='black')
                    self.labelsMovingParams2[i].configure(background=color, foreground='black')
                    self.labelsMovingParams3[i].configure(background=color, foreground='black')
                    self.labelsMovingParams4[i].configure(background=color, foreground='black')
                    self.currently_controlled_vehicle_sensors.append(i)
                    #break
                i = i + 1
        else:
            for index in self.currently_controlled_vehicle_sensors:
                self.videoStreamsFrames[index].configure(background="skyblue4")
                self.videoStreamsInternalFrames[index].configure(background="skyblue4")
                self.videoStreamsTitles[index].configure(background="skyblue4", foreground='white')
                self.videoStreamsSubTitles[index].configure(background="skyblue4", foreground='white')
                self.labelsFps[index].configure(background="skyblue4", foreground='white')
                self.labelsMovingParams1[index].configure(background="skyblue4", foreground='white')
                self.labelsMovingParams2[index].configure(background="skyblue4", foreground='white')
                self.labelsMovingParams3[index].configure(background="skyblue4", foreground='white')
                self.labelsMovingParams4[index].configure(background="skyblue4", foreground='white')

            self.currently_controlled_vehicle_sensors.clear()


    # --- Add spawned vehicle to the video frames tab
    # --- vehicle: controlled vehicle object
    def AddSpawnedVehicle(self, vehicle):
        for vc in vehicle.InstalledVideoCams:
            self.vehicles.append(vehicle)
            self.shown_sensors.append(vc)
        self.vehicleAppended = len(self.vehicles) - 1

    # --- Prepare main motion parameters controls panel
    # --- bgcolor: panel background color
    def prepareMainParamsPanel(self, bgcolor):            

        #self.controlFrame = Frame(self, highlightbackground="black", highlightthickness=1)
        self.controlFrame.grid(sticky="nwse", columnspan=self.maxColumns)
        self.controlFrame.columnconfigure(0, weight=1, uniform="column")
        self.controlFrame.columnconfigure(1, weight=1, uniform="column")
        self.controlFrame.columnconfigure(2, weight=1, uniform="column")

        self.scaleSteering = ExtraScaleControlItem(self.controlFrame, "steering", "st", "STEERING",
                                "trough.png", "slider.png", "lightsteelblue", "midnightblue", 'white', -100, 100, 0, 100,
                                "← / → keys to move, z - fast release", True, True, self.onSteeringChange)
        self.scaleSteering.grid(row=0, column=0, padx=1, pady=1, sticky="nwse")

        self.scaleThrottling = ExtraScaleControlItem(self.controlFrame, "throttling", "tr", "THROTTLING",
                                "trough.png", "slider.png", "lightsteelblue", "midnightblue", 'white', 0, 100, 0, 100,
                                "↑ / ↓ keys to move, x - fast release", True, True, self.onThrottlingChange)
        self.scaleThrottling.grid(row=0, column=1, padx=1, pady=1, sticky="nwse")

        self.scaleBraking = ExtraScaleControlItem(self.controlFrame, "braking", "br", "BRAKING",
                                "trough.png", "slider.png", "lightsteelblue", "midnightblue", 'white', 0, 100, 0, 100,
                                "Q / W keys to move, c - fast release", True, True, self.onBrakingChange)
        self.scaleBraking.grid(row=0, column=2, padx=1, pady=1, sticky="nwse")

    # --- Create extra parameters frame
    # --- title: frame' title
    # --- bgcolor: background color
    # --- var: slider' variable
    def prepareExtraParamsPanel(self, bgcolor):

        #self.extraParamsFrame = Frame(self, background='lightsteelblue', name="extraparamsframe",
        #                 highlightbackground="black", highlightthickness=1)

        self.extraParamsFrame.columnconfigure(0)
        self.extraParamsFrame.columnconfigure(1, weight=1)
        self.extraParamsFrame.columnconfigure(2, weight=1)

        self.extraParamsFrame.grid(sticky="nwse", columnspan=self.maxColumns)

        firstFrame = Frame(self.extraParamsFrame, background='lightsteelblue')
        firstFrame.grid(row=0, column=0)

        manualGearCheckbox = customtkinter.CTkCheckBox(firstFrame, 
                    text = "Use manual gear",  
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.manualGearStatus, onvalue = 1, offvalue = 0,
                    command=self.onManualGearStatusChanged) 
        manualGearCheckbox.grid(row=0, column=0, padx=5, pady=5)

        manualGearFrame = Frame(firstFrame, bg='lightsteelblue')
        manualGearFrame.grid(row=0, column=1)

        manualGearFrame.rowconfigure(0, weight=1)
        manualGearFrame.columnconfigure(0)
        manualGearFrame.columnconfigure(1)

        gearLabel = Label(manualGearFrame, text="Active gear:", bg='lightsteelblue', font=("Roboto", 10))
        gearLabel.grid(row=0, column=0, padx=5, pady=3, sticky="w")
        
        self.mgVar = StringVar()
        self.mgVar.set("1")
        self.manualGearSpinner = Spinbox(manualGearFrame, name="mgsp",
                                         from_=-1, to=5, bg="honeydew2",
                                         textvariable=self.mgVar,
                                         command=self.onGearChange)
        self.manualGearSpinner.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        handBrakeCheckbox = customtkinter.CTkCheckBox(self.extraParamsFrame, text = "Hand brake", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.handBrakeStatus, onvalue = 1, offvalue = 0,
                    command=self.onHandBrakeStatusChanged) 

        handBrakeCheckbox.grid(row=0, column=1)
        
        reverseMovingCheckbox = customtkinter.CTkCheckBox(self.extraParamsFrame, text = "Reverse moving", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.reverseMovingStatus, onvalue = 1, offvalue = 0,
                    command=self.onReverseMovingStatusChanged) 

        reverseMovingCheckbox.grid(row=0, column=2)

        self.onManualGearStatusChanged()

    #---------------------------------
    # --- Controls events handlers ---
    #---------------------------------

    # --- Steering value is changed event handler
    # --- p: new steering value
    def onSteeringChange(self, uuid, p):
        
        turn = "NEUTRAL"

        if float(p) > 0:
            turn = "TURN RIGHT"
        
        if float(p) < 0:
            turn = "TURN LEFT"

        if self.scaleSteering is not None:
            self.scaleSteering.setTitle("STEERING: {0}".format(turn))

        print("------- TURN FOR: {0:.2f}".format(float(p)))    

        if self.carlaServerConnector is not None:
            self.carlaServerConnector.DoAction(1, float(p))

    # --- Throttling value is changed event handler
    # --- p: new throttling value
    def onThrottlingChange(self, uuid, p):
        
        self.throttlingTitle.set("{0:.3f}".format(float(p) / 100))

        if self.carlaServerConnector is not None:
            self.carlaServerConnector.DoAction(2, float(p))

    # --- Braking value is changed event handler
    # --- p: new braking value
    def onBrakingChange(self, uuid, p):
        
        self.brakingTitle.set("{0:.3f}".format(float(p) / 100))
        
        if self.carlaServerConnector is not None:
            self.carlaServerConnector.DoAction(3, float(p))

    # --- Manual gear status check box is changed event handler
    def onManualGearStatusChanged(self):

        checked = self.manualGearStatus.get()

        if(checked == 1):
            self.manualGearSpinner.config(state="normal")
        else:
            self.manualGearSpinner.config(state="disabled")

        self.carlaServerConnector.DoAction(4, checked, self.activeGear)

    # --- Hand brake status check box is changed event handler
    def onHandBrakeStatusChanged(self):

        checked = self.handBrakeStatus.get()
        self.carlaServerConnector.DoAction(6, checked)


    # --- Reverse moving status check box is changed event handler
    def onReverseMovingStatusChanged(self):

        checked = self.reverseMovingStatus.get()
        gear = 1
        if checked == 1:
            #self.manualGearStatus.set(1)
            #self.onManualGearStatusChanged()
            self.mgVar.set("-1")
            gear = -1
        else:
            self.mgVar.set("1")

        self.carlaServerConnector.DoAction(7, checked, gear)

    # --- Manual gear position is changed event handler
    def onGearChange(self):

        self.activeGear = int(self.manualGearSpinner.get())
        self.carlaServerConnector.DoAction(5, self.activeGear)

    #--- Key released event handler
    #--- event: event parameters
    def doKeyboardAction(self, event):

        match event:
            case 1 | 2 | 3: 
                self.scaleSteering.doKeyboardAction(event)
            case 4 | 5 | 6:
                self.scaleThrottling.doKeyboardAction(event - 3)
            case 7 | 8 | 9:
                self.scaleBraking.doKeyboardAction(event - 6)

    # --- CARLA' world tick is done event handler
    # --- params: current moving parameters object
    def onMovingStep(self, params):

        print("-------------- SENSOR INDEX: {}".format(params.sensorIndex))

        if params.velocityKmph is not None:
            self.labelsMovingParams1[params.sensorIndex].configure(text = "V = {0:.1f} kmph ({1:.1f} mps)".format(
                params.velocityKmph, params.velocityMps))
        else:
            self.labelsMovingParams1[params.sensorIndex].configure(text = "V = N/A")

        if params.acceleration is not None:
            self.labelsMovingParams2[params.sensorIndex].configure(
                text = "Acc (m/s²): x={0:.1f} y={1:.1f} z={2:.1f}".format(
                params.acceleration.x, params.acceleration.y, params.acceleration.z))
        else:
            self.labelsMovingParams2[params.sensorIndex].configure(
                text = "Acc (m/s²): x=N/A y=N/A z=N/A")
        
        if params.angleVelocity is not None:             
            self.labelsMovingParams3[params.sensorIndex].configure(
                text = "ω (rad/s): x={0:.1f} y={1:.1f} z={2:.1f}".format(
                params.angleVelocity.x, params.angleVelocity.y, params.angleVelocity.z))
        else:
            self.labelsMovingParams3[params.sensorIndex].configure(
                text = "ω (rad/s): x=N/A y=N/A z=N/A")

        if params.wheelsSteeringAngle is not None:
            self.labelsMovingParams4[params.sensorIndex].configure(
                text = "Awheel (°): {0:.1f}".format(
                params.wheelsSteeringAngle))
        else:
            self.labelsMovingParams4[params.sensorIndex].configure(
                text = "Awheel (°): N/A")

    # --- Defines is provided index belongs to the currently controlled vehicle
    # index: index to be checked
    def IsSensorOnCurrentlyControlledVehicle(self, index):
        for i in self.currently_controlled_vehicle_sensors:
            if index == self.currently_controlled_vehicle_sensors[i]:
                return True;
        return False

    # --- Show received VCU control package values
    # dataPackage: VCU data package to be shown
    def UpdateVCUValues(self, dataPackage):
        msg = "VCU data: WP: {}, WA: {}, AP: {}, BP: {}, CP: {}, GP: {}, BP: {}".format(
                dataPackage[0], dataPackage[1],
                dataPackage[2], dataPackage[3],
                dataPackage[4], dataPackage[5], 
                dataPackage[6])
        self.vcuDataLabel.configure(text=msg)

    # --- Prepare frame to display images processed by prediction unit
    def preparePredictionImageFrame(self):

        titleFrame = Frame(self, background="dodgerblue2", takefocus=True)
        titleFrame.columnconfigure(0, weight=1)
        titleFrame.bind("<Button-1>", self.focusKeyboardPanel)                
        titleFrame.grid(row=1, sticky="nwse")

        self.labelTitle = Label(titleFrame, text="PREDICTION UNIT PROCESSED VIDEO STREAM:", 
                                fg="white", bg="dodgerblue2", font=("Roboto", 11), takefocus=True)
        self.labelTitle.bind("<Button-1>", self.focusKeyboardPanel)                
        self.labelTitle.grid(row=0, column=0, sticky="nwse")

        self.btnImage = PhotoImage(file = "keyboard.png")
        showKeyboardBtn = Button(titleFrame, image = self.btnImage, command=self.onShowKeyboardBtn)
        showKeyboardBtn.grid(row=0, column=1, padx=1, pady=1)

        self.rowconfigure(2, weight=1)
        self.processedImagesFrame = Frame(self, background="skyblue4", takefocus=True)
        self.labelProcessedImagesStream = Label(
            self.processedImagesFrame, background="skyblue4")
        self.labelProcessedImagesStream.bind("<Button-1>", lambda event, i = -1: self.showStreamInOpenCV(i))                
        self.labelProcessedImagesStream.pack(anchor="nw")
        self.processedImagesFrame.bind("<Button-1>", self.focusKeyboardPanel)                
        self.processedImagesFrame.bind("<FocusOut>", self.unfocusKeyboardPanel)
        self.processedImagesFrame.grid(row=2, sticky="nwse", columnspan=self.maxColumns)

    # --- Prediction unit reply is received event handler
    def onPredictionUnitReplyReceived(self, frameID, output_prediction, mode):
        """
        Called each time the prediction unit returns a frame.
        We store last image per mode, and display all stored modes concatenated horizontally.
        """

        # --- pass full prediction to optional OpenCV external viewer thread
        if self.processedImageCVThread is not None:
            self.processedImageCVThread.current_frame = output_prediction

        # --- Save prediction for this mode
        #     Always store raw BGR numpy array
        self.lastPredictionsByMode[mode] = output_prediction.copy()

        # --- keep order consistent: if mode appears first time, append to display order
        if mode not in self.displayOrder:
            self.displayOrder.append(mode)

        # ----------------------------------------------------------
        # Build concatenated image from all stored prediction modes
        # ----------------------------------------------------------

        images_rgb = []

        for m in self.displayOrder:
            img_bgr = self.lastPredictionsByMode[m]

            # Convert to RGB for Tkinter
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            images_rgb.append(rgb)

        # No images? (Should not happen but safety)
        if len(images_rgb) == 0:
            return

        # ----------------------------------------------------------
        # Concatenate horizontally with spacing
        # ----------------------------------------------------------

        spacing = 12  # pixels between images

        # build list with separators
        concat_list = []
        for i, rgb in enumerate(images_rgb):
            concat_list.append(rgb)
            if i != len(images_rgb) - 1:
                sep = np.zeros((rgb.shape[0], spacing, 3), dtype=np.uint8) + 60
                concat_list.append(sep)

        final_rgb = np.concatenate(concat_list, axis=1)

        # ----------------------------------------------------------
        # Convert final image to PIL and display in Tkinter
        # ----------------------------------------------------------
        # Build final PIL image
        pil_img = Image.fromarray(final_rgb)

        # Resize to fit processedImagesFrame
        pil_img = self.ResizeImage(pil_img,
                                   self.processedImagesFrame.winfo_width(),
                                   self.processedImagesFrame.winfo_height(),
                                   pil_img.width / pil_img.height)

        # Convert for tkinter
        tk_img = ImageTk.PhotoImage(pil_img)

        # keep reference alive
        self.processedImage = tk_img
        self.savedProcessedImage = tk_img

        self.labelProcessedImagesStream.configure(image=tk_img)



    # --- Resize image to required scale
    # frame: image to be resized
    # w: image to be resized width
    # h: image to be resized height
    # imageRatio: image width/height ratio
    def ResizeImage(self, frame, w, h, imageRatio):
        
        resizedImage = None
        
        if w > 0 and h > 0:


            if w < h:
                wr = math.floor(w)
                hr = math.floor(w / imageRatio)

                if(hr > h):
                    hr = h
                    wr = math.floor(hr / imageRatio)

                resizedImage = frame.resize((wr, hr))
                
            else:
                wr = math.floor(h * imageRatio)
                hr = math.floor(h)

                if wr > w:
                    wr = w
                    hr = math.floor(wr / imageRatio)

                resizedImage = frame.resize((wr, hr))
        
        return resizedImage

    # --- Stop processed image OpenCV window update thread
    def onProcessedImageCVThreadStopped(self, index):
        self.processedImageCVThread = None

    # --- Show/hide vehicle control panels
    def onShowKeyboardBtn(self):
        if self.isKeyboardControlShown == False:
            self.prepareMainParamsPanel(self.bgcolor)
            self.prepareExtraParamsPanel(self.bgcolor)
            self.isKeyboardControlShown = True
            self.processedImagesFrame.focus_set()
            self.processedImagesFrame.configure(highlightthickness=3, highlightcolor="limegreen")
            self.processedImagesFrame.bind("<KeyPress>", self.onKeyPressed)
        else:
            self.controlFrame.grid_forget()
            self.extraParamsFrame.grid_forget()
            self.isKeyboardControlShown = False
            self.processedImagesFrame.unbind("<KeyPress>")
            self.processedImagesFrame.configure(highlightthickness=0, highlightcolor="blue")
            
    #--- Key pressed event handler
    #--- event: event parameters
    def onKeyPressed(self, event):

        if self.carlaServerConnector.vcu_Connector is None:

            print("KEY IS PRESSED")

            action = -1

            match event.keysym:
                case "Right":
                    action = 1
                case "Left":
                    action = 2
                case "z":
                    action = 3
                case "Up":
                    action = 4
                case "Down":
                    action = 5
                case "x":
                    action = 6
                case "q":
                    action = 7
                case "w":
                    action = 8
                case "c":
                    action = 9

            if action != -1:
                self.doKeyboardAction(action)
                return "break"

    def focusKeyboardPanel(self, event):
        self.processedImagesFrame.focus_set()
        self.processedImagesFrame.configure(highlightthickness=3, highlightcolor="limegreen")
        self.processedImagesFrame.bind("<KeyPress>", self.onKeyPressed)

    def unfocusKeyboardPanel(self, event):
        self.isKeyboardControlShown = False
        self.processedImagesFrame.unbind("<KeyPress>")
        self.processedImagesFrame.configure(highlightthickness=0, highlightcolor="blue")
