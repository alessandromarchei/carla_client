
#================================================
# ===           CARLA emulator client         ===
# ===   -----------------------------------   ===
# === Edit video cam sensor dialog definition ===
#================================================

import tkinter as tk
from tkinter import *
import customtkinter
from turtle import position
from Gui.BasicDialog import BasicDialog
from Model.VideoCam import VideoCam
from tkinter import ttk 
from tkinter import messagebox

class EditVideoCamDlg(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Sensor under edit object
    sensor: None
    
    # Sensor name entry control variable
    sensorName: None

    # Frame size (X-axis) entry control variable
    frameSizeX: None

    # Frame size (Y-axis) entry control variable
    frameSizeY: None

    # Field of vision entry control variable
    fov: None

    # Sensor position (X-axis) entry control variable
    positionX: None

    # Sensor position (Y-axis) entry control variable
    positionY: None

    # Sensor position (Z-axis) entry control variable
    positionZ: None

    # Yaw rotation angle
    rotationYaw: None

    # Kind of postprocessing combobox control variable
    postprocessingKind: None

    # Time in seconds between sensor captures
    frate: None

    # Front sensor flag
    isFront: None

    # Dialog result (True - save changes, otherwise False)
    result: False

    #--------------------
    #--- Constructor  ---
    #--------------------
    def __init__(self, parent, sensor = None):

        self.result = False

        top = self.top = tk.Toplevel(parent)

        if sensor is None:
            top.title("Add sensor")
            self.sensor = VideoCam()
        else:
            top.title("Edit sensor")
            self.sensor = sensor

        # Prepare controls variables    
        self.sensorName = tk.StringVar()
        self.sensorName.set(self.sensor.name)
        self.frameSizeX = tk.StringVar()
        self.frameSizeX.set(self.sensor.frameSizeX)
        self.frameSizeY = tk.StringVar()
        self.frameSizeY.set(self.sensor.frameSizeY)
        self.fov = tk.StringVar()
        self.fov.set(self.sensor.fieldOfVision)
        self.positionX = tk.StringVar()
        self.positionX.set(self.sensor.position.positionX)
        self.positionY = tk.StringVar()
        self.positionY.set(self.sensor.position.positionY)
        self.positionZ = tk.StringVar()
        self.positionZ.set(self.sensor.position.positionZ)
        self.rotationYaw = tk.StringVar()
        self.rotationYaw.set(self.sensor.rotationYaw)
        self.postprocessingKind = tk.StringVar()
        self.postprocessingKind.set(self.sensor.postProcessing)
        self.frate = tk.StringVar()
        self.frate.set(self.sensor.frameRate)
        self.isFront = IntVar(value=self.sensor.isFront)

        top.resizable(False, False)

        # Sensor name
        self.sensorNameTitle = tk.Label(top, text='Sensor name:', font=("Roboto", 10))
        self.sensorNameTitle.pack(anchor="nw", padx=5)
        self.sensorNameEntry = customtkinter.CTkEntry(top, textvariable=self.sensorName, corner_radius=5)
        #self.sensorNameEntry = tk.Entry(top, textvariable=self.sensorName)
        self.sensorNameEntry.pack(anchor="nw", fill="x", padx=10)

        # Sensor position
        positionFrame = Frame(top, padx=5, pady=5)
        positionFrame.pack(anchor="nw")
        positionFrame.rowconfigure(0, weight=1)
        positionFrame.rowconfigure(1, weight=1)
        positionFrame.columnconfigure(0, weight=1)
        positionFrame.columnconfigure(1, weight=1)
        positionFrame.columnconfigure(2, weight=1)

        positionXTitle = tk.Label(positionFrame, text='Position (X)', font=("Roboto", 10))
        positionXTitle.grid(row=0, column=0, sticky="nw")
        vcmd = top.register(self.validateInput)
        positionXEntry = customtkinter.CTkEntry(positionFrame, textvariable=self.positionX,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #positionXEntry = tk.Entry(positionFrame, textvariable=self.positionX,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        positionXEntry.grid(row=1, column=0, padx=5)

        positionYTitle = tk.Label(positionFrame, text='Position (Y)', font=("Roboto", 10))
        positionYTitle.grid(row=0, column=1, sticky="nw")
        vcmd = top.register(self.validateInput)
        positionYEntry = customtkinter.CTkEntry(positionFrame, textvariable=self.positionY,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #positionYEntry = tk.Entry(positionFrame, textvariable=self.positionY,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        positionYEntry.grid(row=1, column=1, padx=5)

        positionZTitle = tk.Label(positionFrame, text='Position (Z):', font=("Roboto", 10))
        positionZTitle.grid(row=0, column=2, sticky="nw")
        vcmd = top.register(self.validateInput)
        positionZEntry = customtkinter.CTkEntry(positionFrame, textvariable=self.positionZ,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #positionZEntry = tk.Entry(positionFrame, textvariable=self.positionZ,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        positionZEntry.grid(row=1, column=2, sticky="nw", padx=5)

        rotationYawTitle = tk.Label(positionFrame, text='Rotation (Yaw):', font=("Roboto", 10))
        rotationYawTitle.grid(row=0, column=3, sticky="nw")
        vcmd = top.register(self.validateInput)
        rotationYawEntry = customtkinter.CTkEntry(positionFrame, textvariable=self.rotationYaw,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #positionZEntry = tk.Entry(positionFrame, textvariable=self.positionZ,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        rotationYawEntry.grid(row=1, column=3, sticky="nw", padx=5)

        # Sensor resolution
        resolutionFrame = Frame(top, padx=5, pady=5)
        resolutionFrame.pack(anchor="nw")
        resolutionFrame.rowconfigure(0, weight=1)
        resolutionFrame.rowconfigure(1, weight=1)
        resolutionFrame.columnconfigure(0, weight=1)
        resolutionFrame.columnconfigure(1, weight=1)
        resolutionFrame.columnconfigure(2, weight=1)

        resolutionXTitle = tk.Label(resolutionFrame, text='Resolution (X)', font=("Roboto", 10))
        resolutionXTitle.grid(row=0, column=0, sticky="nw")
        vcmd = top.register(self.validateInput)
        resolutionXEntry = customtkinter.CTkEntry(resolutionFrame, textvariable=self.frameSizeX,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #resolutionXEntry = tk.Entry(resolutionFrame, textvariable=self.frameSizeX,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        resolutionXEntry.grid(row=1, column=0, sticky="nwse", padx=5)

        resolutionYTitle = tk.Label(resolutionFrame, text='Resolution (Y):', font=("Roboto", 10))
        resolutionYTitle.grid(row=0, column=1, sticky="nw")
        resolutionYEntry = customtkinter.CTkEntry(resolutionFrame, textvariable=self.frameSizeY,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #resolutionYEntry = tk.Entry(resolutionFrame, textvariable=self.frameSizeY,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        resolutionYEntry.grid(row=1, column=1, sticky="nwse", padx=5)

        fovTitle = tk.Label(resolutionFrame, text='Field of vision:', font=("Roboto", 10))
        fovTitle.grid(row=0, column=2, sticky="nw")
        fovEntry = customtkinter.CTkEntry(resolutionFrame, textvariable=self.fov,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #fovEntry = tk.Entry(resolutionFrame, textvariable=self.fov,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        fovEntry.grid(row=1, column=2, padx=5)

        # Frame rate

        frameFrameRate = Frame(top, padx=5, pady=5)
        frameFrameRate.rowconfigure(0, weight=1)
        frameFrameRate.columnconfigure(0)
        frameFrameRate.columnconfigure(1, weight=1)
        frameFrameRate.pack(fill="x", expand=True)

        frameRateTitle = tk.Label(frameFrameRate, text='Time in seconds between sensor captures: ', font=("Roboto", 10))
        frameRateTitle.grid(row=0, column=0, sticky="nw")

        frameRateEntry = customtkinter.CTkEntry(frameFrameRate, textvariable=self.frate,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #frameRateEntry = tk.Entry(frameFrameRate, textvariable=self.frate,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        frameRateEntry.grid(row=0, column=1, padx=5, sticky="nwse")

        # ----------

        # Posprocessing kind frame
        postprocesingFrame = Frame(top, padx=5, pady=5)
        postprocesingFrame.pack(anchor="nw", fill="both", expand=True)
        postprocesingFrame.rowconfigure(0, weight=1)
        postprocesingFrame.rowconfigure(1, weight=1)
        postprocesingFrame.columnconfigure(0, weight=1)

        postprocessTitle = tk.Label(postprocesingFrame, text='Post processing kind:', font=("Roboto", 10))
        postprocessTitle.grid(row=0, column=0, sticky="nw")

        comboboxFrame = Frame(postprocesingFrame, bg="yellow")
        comboboxFrame.grid(row=1, column=0, columnspan=3, 
                           sticky="nwse", padx=5)

        # Create combobox style to set white background for readonly mode
        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly','white')])
        style.map('TCombobox', selectbackground=[('readonly', 'white')])
        style.map('TCombobox', selectforeground=[('readonly', 'black')])

        postprocessCombo = customtkinter.CTkComboBox(comboboxFrame, state="readonly",
            values = ['Depth', 'RGB', 'Optical flow', 'Semantic segmentation', 'Instance segmentation'],
            variable=self.postprocessingKind)
        #postprocessCombo = ttk.Combobox(comboboxFrame, state="readonly",
        #                                textvariable=self.postprocessingKind)

        isFrontCheckbox = customtkinter.CTkCheckBox(top, 
                    text = "Is front sensor", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.isFront, onvalue = 1, offvalue = 0) 
        isFrontCheckbox.pack(fill="both", expand=True, anchor="nw", padx=10)

        postprocessCombo['values'] = ('Depth',  
                          'RGB', 
                          'Optical flow', 
                          'Semantic segmentation',
                          'Instance segmentation') 

        postprocessCombo.pack(fill="both", expand=True)


        # Actions buttons panel
        panelActions = Frame(top)
        panelActions.rowconfigure(0, weight=1)
        panelActions.columnconfigure(0)
        panelActions.columnconfigure(1)
        panelActions.pack()

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=0, sticky="w", padx=10)
        submitButton = ttk.Button(button_border, text=' Apply ', 
            style='W.TButton', command=self.apply)
        submitButton.pack(fill='both')

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        cancelButton = ttk.Button(button_border, text=' Cancel ',
            style='W.TButton', command=self.cancel)
        cancelButton.pack(fill='both')

        self.center_window(top)

    #----------------------
    #--- Service methods
    #----------------------

    # Apply changes button is clicked event handler
    def apply(self):
        self.sensor.name = self.sensorName.get()
        self.sensor.position.positionX = float(self.positionX.get())
        self.sensor.position.positionY = float(self.positionY.get())
        self.sensor.position.positionZ = float(self.positionZ.get())
        self.sensor.rotationYaw = float(self.rotationYaw.get())
        self.sensor.frameSizeX = int(self.frameSizeX.get())
        self.sensor.frameSizeY = int(self.frameSizeY.get())
        self.sensor.fieldOfVision = float(self.fov.get())
        self.sensor.postProcessing = self.postprocessingKind.get()
        self.sensor.isFront = self.isFront.get()

        if self.sensor.isFront:
            if self.sensor.frameSizeX != 640 or self.sensor.frameSizeY != 320:
                res = messagebox.askyesno("Warning", "If you want to use this front sensor for prediction unit, the resolution should be 640*320. Do you want to proceed?",
                                          parent=self.top) 
                if(res == False):
                    return

        self.result = True
        self.top.destroy()

    # Cancel changes button is clicked event handler
    def cancel(self):
        self.top.destroy()

    # Validate entry control input and allow digits and dots only
    def validateInput(self, P):
        return str.isdigit(P) or P == "" or P == "."

