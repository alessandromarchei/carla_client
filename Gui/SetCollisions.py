
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
# https://www.geeksforgeeks.org/python/delete-google-browser-history-using-python/

class SetCollisionsConditionsDlg(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # Dialog result (True - save changes, otherwise False)
    result: False

    # --- Application settings object reference
    app_settings = None

    # --- Use hybrid physics mode checkbox variable
    useHybridMode = 0

    # --- Hybrid mode radius (m)
    hybridRadius = 50

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window reference
    # --- settings: application settings object reference
    def __init__(self, parent, settings):

        self.result = False

        self.app_settings = settings

        self.useHybridMode = IntVar(value = self.app_settings.useHybridPhysicsMode)
        self.hybridRadius = IntVar(value=self.app_settings.hybridModeRadius)

        top = self.top = tk.Toplevel(parent)

        top.resizable(False, False)

        paramsFrame = Frame(top)
        paramsFrame.pack()

        self.hybrydModeCheckbox = customtkinter.CTkCheckBox(paramsFrame, 
                    text = "Use hybrid physics mode", 
                    corner_radius=3, fg_color = ('green', 'white'),
                    variable = self.useHybridMode, onvalue = 1, offvalue = 0) 
        #self.hybrydModeCheckbox = Checkbutton(paramsFrame, 
        #            text = "Use hybrid physics mode", 
        #            variable = self.useHybridMode, onvalue = 1, offvalue = 0) 
        self.hybrydModeCheckbox.pack(anchor="w", padx=5, pady=3)

        radiusFrame = Frame(paramsFrame)
        radiusFrame.pack()

        radiusTitle = Label(radiusFrame, text="Hybrid mode radius (m):", font=("Roboto", 10))
        radiusTitle.grid(row=0, column=0, padx=5)
        radiusEntry = customtkinter.CTkEntry(radiusFrame, textvariable=self.hybridRadius, corner_radius=5)
        #radiusEntry = Entry(radiusFrame, textvariable=self.hybridRadius, width=5)
        radiusEntry.grid(row=0, column=1, sticky="nwse", padx=5)

        # Actions buttons panel
        panelActions = Frame(top)
        panelActions.rowconfigure(0, weight=1)
        panelActions.columnconfigure(0)
        panelActions.columnconfigure(1)
        panelActions.pack()

        button_border = Frame(panelActions, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white')        
        button_border.grid(row=0, column=6, sticky="w", padx=10)
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

    # Apply changes button is clicked event handler
    def apply(self):
        self.result = True
        self.app_settings.useHybridPhysicsMode = self.useHybridMode.get()
        self.app_settings.hybridModeRadius = self.hybridRadius.get()
        self.top.destroy()

    # Cancel changes button is clicked event handler
    def cancel(self):
        self.top.destroy()
