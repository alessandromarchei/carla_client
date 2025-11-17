
#======================================================
# ===             CARLA emulator client             ===
# ===   -----------------------------------------   ===
# ===  Video sensor separate thread implementation  ===
#======================================================

import cv2                      # --- Open CV
import threading
import tkinter as tk
import ctypes

class VideoSensorThreadItem(threading.Thread):

    #-----------------
    #--- Constants ---
    #-----------------

    # --- Display window waiting loop delay
    displayWindowLoopDelay = 5

    #-----------------

    #--------------------------
    #--- Public properties  ---
    #--------------------------
    
    # --- Full-size video stream window is closed event handler
    onThreadStopped: None

    # --- Current video stream frame to be displayed
    current_frame: None

    # --- Video stream should be shown as full screen flag
    isFullScreen = False

    # Sensor frame width
    frameSizeX = 0

    # Sensor frame height
    frameSizeY = 0

    #--------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- previewName: display image window caption
    # --- sensorIndex: currently selected video stream index
    # --- isFullScreen: video stream should be shown as full screen flag
    # --- frameSizeX: sensor frame width
    # --- frameSizeY: sensor frame height
    def __init__(self, previewName, sensorIndex, isFullScreen,
                 frameSizeX, frameSizeY): 

        threading.Thread.__init__(self)
        self.sensorIndex = sensorIndex
        if self.sensorIndex != -1:
            self.previewName = "{} ({})".format(previewName, sensorIndex)
        else: 
            self.previewName = previewName
        self.isFullScreen = isFullScreen
        self.frameSizeX = frameSizeX
        self.frameSizeY = frameSizeY

    # --- Overridden thread "Run" method
    def run(self):
        self.camPreview(self.previewName)

    # --- Open preview window and display video stream until exit
    # --- previewName: display image window caption
    def camPreview(self, previewName):

        cv2.namedWindow(previewName, cv2.WINDOW_NORMAL)

        #cv2.setWindowProperty(previewName, cv2.WND_PROP_TOPMOST, 1)

        if self.isFullScreen:
            cv2.namedWindow(previewName, cv2.WND_PROP_FULLSCREEN)          
            cv2.setWindowProperty(previewName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.resizeWindow(previewName, self.frameSizeX, self.frameSizeY)

        while True:
            
            try:
                if cv2.getWindowProperty(previewName, cv2.WND_PROP_VISIBLE) < 1:
                    break

                cv2.imshow(previewName, self.current_frame)

                key = cv2.waitKey(self.displayWindowLoopDelay)

                if key == 27:  # exit on ESC
                    cv2.destroyWindow(previewName)
                    break
            
            except Exception as e:                
                print("Exception in CV2: {}".format(e))
        
        if self.onThreadStopped is not None:
            self.onThreadStopped(self.sensorIndex)
