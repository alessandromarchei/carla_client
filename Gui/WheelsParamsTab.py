
#===============================================
# ===          CARLA emulator client         ===
# ===   ----------------------------------   ===
# ===  Turn parameters tab panel definition  ===
#===============================================

from tkinter import *
from tkinter import ttk

from Gui.ScrollableFrame import ScrollFrame
from Gui.WheelParamsPanel import WheelParamsPanelEditor

# https://carla.readthedocs.io/en/latest/python_api/#carla.VehicleControl
class WheelsParamsTabItem(Frame):

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- parent: parent window object
    # --- bgcolor: panel background color
    def __init__(self, parent, bgcolor):
        
        super().__init__(parent, bg=bgcolor,
            highlightbackground="black", highlightthickness=1)
       
        self.prepareWheelsPanels(bgcolor)

        applyButton = Button(self, text="  Apply  ", 
                             bg="skyblue1", fg="black")

        applyButton.pack(anchor="e", padx=5, pady=5)
    
    # --- Prepare controls panel
    # --- bgcolor: panel background color
    def prepareWheelsPanels(self, bgcolor):            

        wheelsFrame = ScrollFrame(self, name="wheels")
        wheelsFrame.pack(anchor="n", fill="both", expand=True)

        leftForwardWheel = WheelParamsPanelEditor(wheelsFrame.viewPort, "white", "LEFT FORWARD WHEEL", "lfw", name="uUU1")        
        leftForwardWheel.pack(anchor="w", fill="x", padx=5, pady=5)

        rightForwardWheel = WheelParamsPanelEditor(wheelsFrame.viewPort, "white", "RIGHT FORWARD WHEEL", "rfw", name="uUU2")        
        rightForwardWheel.pack(anchor="w", fill="x", padx=5, pady=5)

        leftBackwardWheel = WheelParamsPanelEditor(wheelsFrame.viewPort, "white", "LEFT BACKWARD WHEEL", "lbw", name="uUU3")        
        leftBackwardWheel.pack(anchor="w", fill="x", padx=5, pady=5)

        rightBackwardWheel = WheelParamsPanelEditor(wheelsFrame.viewPort, "white", "RIGHT BACKWARD WHEEL", "rbw", name="uUU4")        
        rightBackwardWheel.pack(anchor="w", fill="x", padx=5, pady=5)
