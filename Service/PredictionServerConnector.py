
#================================================
# ===          CARLA emulator client          ===
# ===   ------------------------------------  ===
# ===     External vehicle control device     ===  
# ===         connector implementation        ===
#================================================

from ctypes import sizeof
from io import BytesIO
import socket
import threading
import time
from PIL import Image
import numpy as np
import struct
import cv2
import numpy as np

from Service import SpawnedSensor
from Service.SpawnedSensor import SpawnedSensorItem

# --- https://stackoverflow.com/questions/53285659/how-can-i-wait-until-i-receive-data-using-a-python-socket

class PredictionUnitConnector(object):

    #----------------------------
    #--- Constants (commands) ---
    #----------------------------
        
    CMD_REGISTER = 1
    CMD_UNREGISTER = 2
    CMD_IMGSTART_TRANSMISSION = 3
    CMD_IMGSTOP_TRANSMISION = 5
    CMD_IMGEVALUATION = 6

    #---------------------------------------
    #--- Constants (commands parameters) ---
    #---------------------------------------
    DET_RCVFMT640 = 100

    #---------------------------
    #--- Constants (replies) ---
    #---------------------------
    RSP_REGDENIED = -1
    RSP_REGISTERED = 10
    RSP_UNREGISTERED = 11

    #---------------------------
    #--- Constants (formats) ---
    #---------------------------
    REGISTRATION_CMD_FORMAT = "ii"
    REGISTRATION_REPLY_FORMAT = "ii"
    START_TRANSMISSION_CMD_FORMAT = "iiiii"
    START_TRANSMISSION_REPLY_FORMAT = "ii"
    IMGEVALUATION_REPLY_FORMAT = "ii"

    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- Connection socket object
    socket = None

    # --- Stop listening request sign
    stopRequested = False

    # --- 
    carlaServiceConnector: None

    # --- Is client registered on remote device flag
    isRegistered = False;

    # --- Successfully sent images counter
    sentImagesCounter = 1

    # --- Send image cycle is in progress flag
    isSendImageInProgress = False

    #-------------------------------------------
    #--- Public properties (events handlers) ---
    #-------------------------------------------

    # --- Connection to CARLA server attempt is completed event handler
    OnDataPackageReceived = None

    # --- Default constructor 
    def __init__(self, carlaServiceConnector):

        self.socket = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        self.carlaServiceConnector = carlaServiceConnector

    # --- Connect to requested server and port
    # --- Required host address (Dns name)
    # --- Required remote port number
    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
            self.stopRequested = False
            print('Successful Connection')
            return True
        except Exception as ex:
            print('Connection Failed: {}'.format(ex))
            return False

    # --- Disconnect from server
    def disconnect(self):
        if self.socket != None:
            try:
                if self.isRegistered == True:
                    msg = struct.pack(self.REGISTRATION_CMD_FORMAT, 
                        *[self.CMD_UNREGISTER, 0])
                    self.socket.send(msg)
                self.stopRequested = True
                self.socket.close()
            except:
                print('Disconnection Failed')

    # --- Send image to prediction calculation facade
    # data: image to be sent to process
    # imgWidth: image to be sent width
    # imgHeight: image to be sent height
    def sendDataForPrediction(self, data, imgWidth, imgHeight):
        print("Sending data to TPU. Start thread")
        listeningThread = threading.Thread(target=self.sendDataForPredictionThread(data, imgWidth, imgHeight), 
            daemon=True)
        listeningThread.start()

    # --- Send image to prediction calculation thread
    # data: image to be sent to process
    # imgWidth: image to be sent width
    # imgHeight: image to be sent height
    def sendDataForPredictionThread(self, data, imgWidth, imgHeight):

        # --- Check if the process is blocked now
        if self.isSendImageInProgress == True:
            return

        self.isSendImageInProgress = True

        try:

            # --- Register on remote unit if not registered yet
            
            if self.isRegistered == False:
            
                print("*********** SENDING REGISTRATION REQUEST!")

                msg = struct.pack(self.REGISTRATION_CMD_FORMAT, 
                    *[self.CMD_REGISTER, self.DET_RCVFMT640])

                self.socket.send(msg)
                
                reply_raw = self.socket.recv(struct.calcsize(self.REGISTRATION_REPLY_FORMAT))

                reply = struct.unpack(self.REGISTRATION_REPLY_FORMAT, reply_raw)

                # --- Check registration result
                if reply[0] == self.CMD_REGISTER:
                    if reply[1] == self.RSP_REGISTERED:
                        print("*********** CLIENT REGISTERED!")
                        self.isRegistered = True
                    else:
                        return
                else:
                    return
            
            # --- End of registration procedure
                
            # --- Send preparation command 

            print("1. ******* SENDING IMAGE PARAMS")

            msg = struct.pack(self.START_TRANSMISSION_CMD_FORMAT, 
                *[self.CMD_IMGSTART_TRANSMISSION, self.sentImagesCounter,
                  imgWidth, imgHeight, 4])

            self.socket.send(msg)

            reply_raw = self.socket.recv(struct.calcsize(self.REGISTRATION_REPLY_FORMAT))

            reply = struct.unpack(self.START_TRANSMISSION_REPLY_FORMAT, reply_raw)

            # --- Check preparation request result
            if reply[0] == self.CMD_IMGSTART_TRANSMISSION:

                print("2. ******* IMAGE PARAMS SENT")

                # --- If result is OK, send image itself
                
                print("3. ******* SENDING IMAGE BYTES")
    
                # --- Model expects RGB (3 bytes) image array
                # --- Convert Carla image (4 bytes) to 3 bytes RGB

                prepared_image = np.ascontiguousarray(
                    SpawnedSensorItem.to_rgb_array(data, imgWidth, imgHeight))

                img_size = prepared_image.size

                self.socket.send(prepared_image)

                reply_raw = self.socket.recv(struct.calcsize(self.START_TRANSMISSION_REPLY_FORMAT))

                reply = struct.unpack(self.START_TRANSMISSION_REPLY_FORMAT, reply_raw)

                if reply[0] == self.CMD_IMGSTOP_TRANSMISION:

                    print("4. ******* IMAGE BYTES SENT")

                    reply_mask = self.socket.recv(imgWidth * imgHeight * 1)
                    
                    print("5. ******* REPLY MASK RECEIVED")

                    # --- Check result of sending image
                    reply_raw = self.socket.recv(struct.calcsize(self.IMGEVALUATION_REPLY_FORMAT))

                    reply = struct.unpack(self.IMGEVALUATION_REPLY_FORMAT, reply_raw)

                    if reply[0] == self.CMD_IMGEVALUATION:

                        print("6. ******* IMAGE EVALUATED")

                        input_frame = np.uint8(SpawnedSensorItem.to_rgb_array(
                            data, imgWidth, imgHeight))

                        input_mask = np.frombuffer(reply_mask, dtype=np.uint8)

                        prepared_array = np.ndarray((imgHeight, imgWidth), np.uint8, input_mask)

                        masked_image = self.add_mask_segmentation(
                            input_frame, prepared_array, 0.5)

                        pil_image = Image.fromarray(masked_image)

                        cv2img = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)
                        
                        # --- Display masked image in the main window
                        self.carlaServiceConnector.PredictionUnitReplyReceived(
                            cv2img, pil_image, imgWidth / imgHeight)
   
                        print("7. ******* RECEIVED MASK APPLIED")

                        self.sentImagesCounter = self.sentImagesCounter + 1

        except Exception as ex:
            print("Reply processing exception: {}".format(ex))

        self.isSendImageInProgress = False

    # === ALESSANDRO' CODE TO APPLY MASK

    def mask_segmentation(self, prediction):
        """
        Generate RGB visualization from prediction mask.
        Background = orange, class 1 = purple, class 2 = green.
        """
        shape = prediction.shape
        vis_predict_object = np.zeros((shape[0], shape[1], 3), dtype="uint8")
 
        # Default background → orange
        vis_predict_object[:, :, 0] = 255
        vis_predict_object[:, :, 1] = 93
        vis_predict_object[:, :, 2] = 61
 
        # Class 1 (object) → purple
        fg = np.where(prediction == 1)
        vis_predict_object[fg[0], fg[1], :] = (145, 28, 255)
 
        # Class 2 (road/drivable surface) → green
        road = np.where(prediction == 2)
        vis_predict_object[road[0], road[1], :] = (0, 255, 0)
 
        return vis_predict_object
 
 
    def add_mask_segmentation(self, input_frame, prediction, alpha):
        """
        Overlay segmentation mask on input frame with given alpha transparency.
        Target size = prediction size
        """
        mask = self.mask_segmentation(prediction)
 
        # Resize input frame to prediction shape
        input_frame_resized = cv2.resize(input_frame, (mask.shape[1], mask.shape[0]))
 
        # Blend
        output_frame = cv2.addWeighted(mask, alpha, input_frame_resized, 1 - alpha, 0)
        return output_frame
 
    # ====================================
