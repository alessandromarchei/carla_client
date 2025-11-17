
#================================================
# ===           CARLA emulator client         ===
# ===   -----------------------------------   ===
# === Edit video cam sensor dialog definition ===
#================================================

import tkinter as tk
import customtkinter
from tkinter import *
from tkinter import ttk
# --- Python 3.10 environment MAX is required
# --- 3.11 one is not supported yet
import carla

from Gui.BasicDialog import BasicDialog 

# https://carla.readthedocs.io/en/0.9.15/tuto_first_steps/
class AddVehicle(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Dialog result (True - save changes, otherwise False)
    result: False

    selectVehicleCombo = None

    #
    selectedVehicleObj = None

    #
    name: None

    #
    selectedVehicle = None

    #
    vehicles = None

    #--------------------
    #--- Constructor  ---
    #--------------------

    def __init__(self, parent, vehicles):

        self.result = False

        self.vehicles = vehicles

        self.name = tk.StringVar()

        self.selectedVehicle = tk.StringVar()

        if (self.vehicles is not None) and (len(self.vehicles) > 0):
            self.selectedVehicleObj = self.vehicles[0]

        top = self.top = tk.Toplevel(parent)

        top.resizable(False, False)

        nameTitle = tk.Label(top, text='Vehicle nick name:', font=("Roboto", 10))
        nameTitle.pack(anchor="nw", padx=5)
        nameEntry = customtkinter.CTkEntry(top, textvariable=self.name, corner_radius=5)
        #nameEntry = tk.Entry(top, textvariable=self.name)
        nameEntry.pack(expand=True, fill="x", padx=10)

        # Selected vehicle frame
        selectVehicleFrame = Frame(top, padx=5, pady=5)
        selectVehicleFrame.pack(anchor="nw", fill="both", expand=True)
        selectVehicleFrame.rowconfigure(0, weight=1)
        selectVehicleFrame.rowconfigure(1, weight=1)
        selectVehicleFrame.columnconfigure(0, weight=1)

        selectVehicleTitle = tk.Label(selectVehicleFrame, text='Select vehicle to work with:    ', font=("Roboto", 10))
        selectVehicleTitle.grid(row=0, column=0, sticky="nw")

        comboboxFrame = Frame(selectVehicleFrame, bg="yellow")
        comboboxFrame.grid(row=1, column=0, columnspan=3, 
                           sticky="nwse", padx=5)

        # Create combobox style to set white background for readonly mode
        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly','white')])
        style.map('TCombobox', selectbackground=[('readonly', 'white')])
        style.map('TCombobox', selectforeground=[('readonly', 'black')])

        self.selectVehicleCombo = customtkinter.CTkComboBox(comboboxFrame, state="readonly",
                                        variable=self.selectedVehicle, command=self.onVehicleSelected)
        #self.selectVehicleCombo = ttk.Combobox(comboboxFrame, state="readonly",
        #                                textvariable=self.selectedVehicle)

        if self.vehicles is not None:
            displayedVehicles = list()

            # Loop through retrieved items
            for vehicle in vehicles:
                displayedVehicles.append("{} {}".format(vehicle.Manufacturer, vehicle.Model))

            self.selectedVehicle.set(displayedVehicles[0])

            self.selectVehicleCombo.configure(values = displayedVehicles)  
            #self.selectVehicleCombo['values'] = displayedVehicles  

        #self.selectVehicleCombo.bind('<<ComboboxSelected>>', self.onVehicleSelected) 
        self.selectVehicleCombo.pack(fill="both", expand=True)

        # Actions buttons panel
        panelActions = Frame(top)
        panelActions.rowconfigure(0, weight=1)
        panelActions.columnconfigure(0)
        panelActions.columnconfigure(1)
        panelActions.pack()

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=0, sticky="w", padx=5)        
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

    # Select vehicle combo selection changed event handler
    # event: event parameters
    def onVehicleSelected(self, event):
        index = 0
        for vehicle in self.vehicles:
            if "{} {}".format(vehicle.Manufacturer, vehicle.Model) == event:
                self.selectedVehicleObj = vehicle
                return
        #selectedIndex = self.selectVehicleCombo.current()
        #self.selectedVehicleObj = self.vehicles[selectedIndex]

    # Apply changes button is clicked event handler
    def apply(self):
        self.result = True
        self.selectedVehicleObj.Name = self.name.get()
        self.top.destroy()

    # Cancel changes button is clicked event handler
    def cancel(self):
        self.top.destroy()
