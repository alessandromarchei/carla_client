
#================================================
# ===           CARLA emulator client         ===
# ===   -----------------------------------   ===
# === Edit video cam sensor dialog definition ===
#================================================

import tkinter as tk
from tkinter import *
from tkinter import ttk
import carla

from Gui.BasicDialog import BasicDialog 

# https://carla.readthedocs.io/en/0.9.15/tuto_first_steps/
class TopDownViewDlg(BasicDialog):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # --- Application-wide Carla connection service object reference
    carlaService = None

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window reference
    # --- carlaService: Carla connection service object reference
    def __init__(self, parent, carlaService):

        self.carlaService = carlaService

        self.carlaService.OnTopDownImageReceived = self.OnTopDownImageReceived

        top = self.top = tk.Toplevel(parent)

        top.protocol("WM_DELETE_WINDOW", self.on_close)

        top.resizable(False, False)

        commonFrame = Frame(top)
        commonFrame.pack()

        commonFrame.columnconfigure(0, minsize=640)
        commonFrame.rowconfigure(0, minsize=320)

        labelVideoStreamViewer = Label(commonFrame, image=None, 
                                       background='skyblue4', 
                                       #width=640, height=320,
                                       font=("Roboto", 10))
        labelVideoStreamViewer.grid(column=0)

        self.center_window(top)

    # --- New image is recieved event handler
    # image: new image to be displayed
    def OnTopDownImageReceived(self, image):
        print("Display top-down image")

    # --- Close window event handler
    def on_close(self):
        self.carlaService.OnTopDownImageReceived = None
        print("Closing window")
        self.top.destroy()


