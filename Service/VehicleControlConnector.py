
#================================================
# ===          CARLA emulator client          ===
# ===   ------------------------------------  ===
# ===     External vehicle control device     ===  
# ===         connector implementation        ===
#================================================

import socket
import threading
import time
import numpy as np
import struct

# --- https://stackoverflow.com/questions/53285659/how-can-i-wait-until-i-receive-data-using-a-python-socket

class VehicleControlUnitConnector(object):

    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- Connection socket object
    socket = None

    # --- Stop listening request sign
    stopRequested = False

    # --- Expected format of the received package
    expectedPackageFormat = ""

    #-------------------------------------------
    #--- Public properties (events handlers) ---
    #-------------------------------------------

    # --- Connection to CARLA server attempt is completed event handler
    OnDataPackageReceived = None

    # --- Default constructor 
    # expectedPackageFormat: expected format of the received package
    def __init__(self, expectedPackageFormat):

        self.socket = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        self.expectedPackageFormat = expectedPackageFormat
    
    # --- Connect to requested server and port
    # --- Required host address (Dns name)
    # --- Required remote port number
    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
            self.stopRequested = False
            print('Successful Connection')
            listeningThread = threading.Thread(target=self.doRead, 
                daemon=True)
            listeningThread.start()
            return True
        except Exception as ex:
            print('Connection Failed: {}'.format(ex))
            return False

    # --- Disconnect from server
    def disconnect(self):
        if self.socket != None:
            try:
                self.stopRequested = True
                self.socket.close()
            except:
                print('Disconnection Failed')

    # --- Read the data from remote server
    def doRead(self):

        while True:
        
            if self.stopRequested == True:
                break;

            try:

                dataPackage = self.socket.recv(
                    struct.calcsize(self.expectedPackageFormat))

                if dataPackage is not None:
                    print("VCU raw data: {}".format(dataPackage))

                    # -----------------
                    decodedData = struct.unpack(
                        self.expectedPackageFormat, dataPackage)

                    if self.OnDataPackageReceived is not None:
                        self.OnDataPackageReceived(decodedData)
                else:
                    print("No data recieved")
                    
            except Exception as ex:
                print("Exception reading control unit: {}".format(ex))

                if self.stopRequested == True:
                    break;
            
            #time.sleep(0.01)

