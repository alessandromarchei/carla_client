
#===================================================
# ===           CARLA emulator client            ===
# ===   --------------------------------------   ===
# === Vehicle initial spawning dialog definition ===
#===================================================

import tkinter as tk
from tkinter import *
from tkinter import ttk
import customtkinter

from Gui.BasicDialog import BasicDialog 

class SpawnVehicle(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Dialog result (True - save changes, otherwise False)
    result: False

    # --- Currently selected vehicle object
    selectedVehicle = None

    # --- Application settings object reference
    collisionDef = None

    # --- Vehicle behavior profile name
    behaviorName = None

    # --- Ignore traffic lights checkbox variable
    ignoreTrafficLights = 0

    # --- Ignore stop signs checkbox variable
    ignoreStopSigns = 0

    # --- Ignore other vehicles checkbox variable
    ignoreVehicles = 0

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window object reference
    # --- vehicle: vehicle to be spawned
    # --- collision: collision settings object reference
    def __init__(self, parent, vehicle):

        self.result = False

        self.selectedVehicle = vehicle

        self.behaviorName = StringVar(value='cautious')

        top = self.top = tk.Toplevel(parent)

        top.resizable(False, False)

        positionTitle = tk.Label(top, text='{} VEHICLE BEHAVIOUR:'.format(vehicle.Name), font=("Roboto", 10))
        positionTitle.pack(anchor="nw", padx=5, pady=5)

        behaviorCombo = customtkinter.CTkComboBox(top, state="readonly", 
            values = ['cautious', 'normal', 'aggressive'],
            variable=self.behaviorName)

        #behaviorCombo = ttk.Combobox(top, state="readonly",
        #                                textvariable=self.behaviorName)

        #behaviorCombo['values'] = ('cautious',  
        #                  'normal', 
        #                  'aggressive') 

        behaviorCombo.pack(fill="x", expand=True, padx=5)

        self.ignoreTrafficLights = IntVar(value=0)
        self.ignoreStopSigns = IntVar(value=0)
        self.ignoreVehicles = IntVar(value=0)


        ignoreTrafficLightsCheckbox = customtkinter.CTkCheckBox(top, 
                    text = "Ignore traffic lights", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.ignoreTrafficLights, onvalue = 1, offvalue = 0) 
        #ignoreTrafficLightsCheckbox = Checkbutton(top, 
        #            text = "Ignore traffic lights", 
        #            variable = self.ignoreTrafficLights, onvalue = 1, offvalue = 0) 
        ignoreTrafficLightsCheckbox.pack(anchor="w", expand=True, padx=5, pady=3)

        ignoreStopSignsCheckbox = customtkinter.CTkCheckBox(top, 
                    text = "Ignore stop signs", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.ignoreStopSigns, onvalue = 1, offvalue = 0) 
        #ignoreStopSignsCheckbox = Checkbutton(top, 
        #            text = "Ignore stop signs", 
        #            variable = self.ignoreStopSigns, onvalue = 1, offvalue = 0) 
        ignoreStopSignsCheckbox.pack(anchor="w", expand=True, padx=5, pady=3)

        ignoreVehiclesCheckbox = customtkinter.CTkCheckBox(top, 
                    text = "Ignore vehicles", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.ignoreVehicles, onvalue = 1, offvalue = 0) 
        #ignoreVehiclesCheckbox = Checkbutton(top, 
        #            text = "Ignore vehicles", 
        #            variable = self.ignoreVehicles, onvalue = 1, offvalue = 0) 
        ignoreVehiclesCheckbox.pack(anchor="w", expand=True, padx=5, pady=3)

        # Actions buttons panel
        panelActions = Frame(top)
        panelActions.rowconfigure(0, weight=1)
        panelActions.columnconfigure(0)
        panelActions.columnconfigure(1)
        panelActions.pack()

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=0, sticky="w", padx=10)        
        spawnButton = ttk.Button(button_border, text=' Spawn ', 
            style='W.TButton', command=self.apply)
        spawnButton.pack(fill='both')

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=1, sticky="w", padx=10, pady=10)        
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
