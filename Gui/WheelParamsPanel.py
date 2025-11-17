
#========================================================
# ===               CARLA emulator client             ===
# ===   -------------------------------------------   ===
# ===  Single wheel parameters editor implementation  ===
#========================================================

from doctest import master
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

from Gui.ExtraScaleControl import ExtraScaleControlItem

class WheelParamsPanelEditor(Frame):

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window object
    # --- bgcolor: panel background color
    # --- title: panel title
    # --- identifier: panel identifier
    def __init__(self, parent, bgcolor, title, identifier, name):
        
        super().__init__(parent, bg=bgcolor, name=name,
                         highlightbackground="black", highlightthickness=1)

        self.rowconfigure(0)
        self.rowconfigure(1)
        self.rowconfigure(2)
        self.rowconfigure(3)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        labelTitle = Label(self, anchor="nw", text=title, bg=bgcolor,
                           font=("Roboto", 11), padx=5)
        labelTitle.grid(row=0, column=0, columnspan=3, sticky="w")

        tireFrictionPanel = ExtraScaleControlItem(self, "tire", identifier, "Tire friction",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        tireFrictionPanel.grid(row=1, column=0, sticky="nwse", padx=5, pady=5)

        dampingPanel = ExtraScaleControlItem(self, "damping", identifier, "Damping rate",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        dampingPanel.grid(row=1, column=1, sticky="nwse", padx=5, pady=5)

        maxSteerPanel = ExtraScaleControlItem(self, "maxsteer", identifier, 'Max steer angle (degree)',
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        maxSteerPanel.grid(row=1, column=2, sticky="nwse", padx=5, pady=5)

        radiusPanel = ExtraScaleControlItem(self, "radius", identifier, "Radius (cm)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        radiusPanel.grid(row=1, column=3, sticky="nwse", padx=5, pady=5)

        maxBrakeTorquePanel = ExtraScaleControlItem(self, "maxbraketorque", identifier, "Max brake torque (N*m)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        maxBrakeTorquePanel.grid(row=2, column=0, sticky="nwse", padx=5, pady=5)
        
        maxHandBrakeTorquePanel = ExtraScaleControlItem(self, "maxhandbraketorque", identifier, "Max hand brake torgue (N*m)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        maxHandBrakeTorquePanel.grid(row=2, column=1, sticky="nwse", padx=5, pady=5)

        longStiffPanel = ExtraScaleControlItem(self, "longstiff", identifier, "Long stiffness (kg/rad)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        longStiffPanel.grid(row=2, column=2, sticky="nwse", padx=5, pady=5)

        latStiffPanel = ExtraScaleControlItem(self, "latstiff", identifier, "Lat stiffness (kg/rad)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        latStiffPanel.grid(row=2, column=3, sticky="nwse", padx=5, pady=5)

        latStiffMaxLoadPanel = ExtraScaleControlItem(self, "lattiffmaxload", identifier, "Lat stiffness max load",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        latStiffMaxLoadPanel.grid(row=3, column=0, sticky="nwse", padx=5, pady=5)

        positionXPanel = ExtraScaleControlItem(self, "positionx", identifier, "Position (X-axis)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        positionXPanel.grid(row=3, column=1, sticky="nwse", padx=5, pady=5)

        positionYPanel = ExtraScaleControlItem(self, "positiony", identifier, "Position (Y-axis)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        positionYPanel.grid(row=3, column=2, sticky="nwse", padx=5, pady=5)

        positionZPanel = ExtraScaleControlItem(self, "positionz", identifier, "Position (Z-axis)",
                                "trough.png", "slider.png", "white", "lemonchiffon", 'black', 0, 100, 0, 1, "")
        positionZPanel.grid(row=3, column=3, sticky="nwse", padx=5, pady=5)

