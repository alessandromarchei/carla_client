
#==================================================
# ===           CARLA emulator client           ===
# ===   -------------------------------------   ===
# === Set obstacle parameters dialog definition ===
#==================================================

import tkinter as tk
import customtkinter
from tkinter import *
from tkinter import ttk
# --- Python 3.10 environment MAX is required
# --- 3.11 one is not supported yet
import carla

from Gui.BasicDialog import BasicDialog 

# https://carla.readthedocs.io/en/0.9.15/tuto_first_steps/
class SetObstacleParamsDlg(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Dialog result (True - save changes, otherwise False)
    result: False
    
    # Selected obstacle kind
    obstacleKind = None
                
    # Entered obstacle distance (m)
    obstacleDistance = 0
                
    # Entered obstacle angle (degrees)
    obstacleAngle = 0

    # Move obstacle after placing flag
    moveObstacle = 0

    #--------------------
    #--- Constructor  ---
    #--------------------

    def __init__(self, parent):

        self.result = False

        top = self.top = tk.Toplevel(parent)

        top.resizable(False, False)

        self.obstacleKind = StringVar()
        self.obstacleDistance = StringVar()
        self.obstacleDistance.set("10.0")
        self.obstacleAngle = StringVar()
        self.obstacleAngle.set("5.0")
        self.moveObstacle = IntVar()
        self.moveObstacle.set(0)

        obstacleFrame = Frame(top, padx=5, pady=5)
        obstacleFrame.pack(anchor="nw", fill="both", expand=True)
        obstacleFrame.rowconfigure(0, weight=1)
        obstacleFrame.rowconfigure(1, weight=1)
        obstacleFrame.columnconfigure(0, weight=1)

        kindTitle = tk.Label(obstacleFrame, text='Obstacle kind:', font=("Roboto", 10))
        kindTitle.grid(row=0, column=0, sticky="nw")

        comboboxFrame = Frame(obstacleFrame, bg="yellow")
        comboboxFrame.grid(row=1, column=0, columnspan=3, 
                           sticky="nwse", padx=5)

        # Create combobox style to set white background for readonly mode
        style = ttk.Style()
        style.map('TCombobox', fieldbackground=[('readonly','white')])
        style.map('TCombobox', selectbackground=[('readonly', 'white')])
        style.map('TCombobox', selectforeground=[('readonly', 'black')])

        self.selectObstacleCombo = ttk.Combobox(comboboxFrame, state="readonly",
                                        textvariable=self.obstacleKind)

        self.kinds = list()
        self.kinds.append("vehicle")
        self.kinds.append("pedestrian")
        self.obstacleKind.set(self.kinds[0])
        self.selectObstacleCombo['values'] = self.kinds  

        self.selectObstacleCombo.bind('<<ComboboxSelected>>', self.onKindSelected) 
        self.selectObstacleCombo.pack(fill="both", expand=True)

        distanceTitle = tk.Label(top, text='Distance to obstacle (m):', font=("Roboto", 10))
        distanceTitle.pack(anchor="nw", padx=5)

        vcmd = top.register(self.validateInput)
        distanceEntry = customtkinter.CTkEntry(top, textvariable=self.obstacleDistance,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #distanceEntry = tk.Entry(top, textvariable=self.obstacleDistance,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        distanceEntry.pack(anchor="nw", fill="x", padx=5)

        angleTitle = tk.Label(top, text='Obstacle azimuth (degrees):', font=("Roboto", 10))
        angleTitle.pack(anchor="nw", padx=5)

        angleEntry = customtkinter.CTkEntry(top, textvariable=self.obstacleAngle,
                                    validate='all', validatecommand=(vcmd, '%P'), corner_radius=5)
        #angleEntry = tk.Entry(top, textvariable=self.obstacleAngle,
        #                            validate='all', validatecommand=(vcmd, '%P'))
        angleEntry.pack(anchor="nw", fill="x", padx=5)

        syncModeCheckbox = customtkinter.CTkCheckBox(top, 
            text = "Let obstacle to move", 
            corner_radius=3, fg_color = ('green', 'white'),
            variable = self.moveObstacle, onvalue = 1, offvalue = 0) 

        #syncModeCheckbox = Checkbutton(top, 
        #    name="mgcb", text = "Let obstacle to move", 
        #    variable = self.moveObstacle, onvalue = 1, offvalue = 0) 
        syncModeCheckbox.pack(anchor="nw", fill="x", padx=5, pady=5)

        # Check-box to move obstacle

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
    def onKindSelected(self, event):
        selectedIndex = self.selectObstacleCombo.current()
        self.obstacleKind.set(self.kinds[selectedIndex])

    # Apply changes button is clicked event handler
    def apply(self):
        self.result = True
        self.top.destroy()

    # Cancel changes button is clicked event handler
    def cancel(self):
        self.top.destroy()

    # Validate entry control input and allow digits and dots only
    def validateInput(self, P):
        return str.isdigit(P) or P == "" or P == "."
