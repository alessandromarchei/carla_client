from TCP.ServerSender import ServerSender
from TCP.ServerReceiver import ServerReceiver
from TCP.Buffer import BlockingQueue
import threading
import time
import cv2
import sys
import os
import numpy as np
from PIL import Image
import cmapy
import struct
from Service.Enumerations import DataType, ImageModality

#TODO: test as well the DEPTH pipeline (for now only the SEGMENTATION model is tested)

"""
This PU block takes as input the raw images from CARLA engine (carla processor service) and:
    - 1) converts into good format if needed
    - 2) prepares metatada to send to the TX 
    - 3) sends to the embedded side (for AI inference) via TCP sender
    - 4) receives the prediction results from the RX TCP receiver
    - 5) applies postprocessing (visualization) to the output, based on the model type received
"""

DEFAULT_TX_PORT = 8080
DEFAULT_RX_PORT = 8081


#sender metadata (all 32 bits unsigned int, littl endian, for being compatible with embedded side)

HEADER_FMT_TX = "<IIIIIII"   # frame_id, height, width, channels, dtype, total_bytes, mode
HEADER_FMT_RX = "<IIIIIII"  # frame_id, height, width, channels, dtype, total_bytes, mode
#mode = output modality (segmentation, depth, etc)

class PredictionUnitConnector(object):

    def __init__(self, carlaServiceConnector=None):
        print("[PU Connector] init")
        self.carlaServiceConnector = carlaServiceConnector  #passed from caller so we can call the callback function from here

        self.sender_queue = None
        self.matching_queue = None

        self.sender = None
        self.receiver = None

        self.sender_framecounter = 0

        self.running = False
        self.receiver_thread = None

    # ----------------------------------------------------------
    # CONNECT
    # ----------------------------------------------------------
    def connect(self, tx_port=DEFAULT_TX_PORT, rx_port=DEFAULT_RX_PORT):
        print("[PU Connector] Connecting...")

        try:
            # Thread-safe queues
            self.sender_queue = BlockingQueue()    # frames to send
            self.matching_queue = BlockingQueue()  # original frames to be matched

            # Create sender (async)
            self.sender = ServerSender(
                port=tx_port,
                input_queue=self.sender_queue,
                sent_queue=self.matching_queue,
            )

            # Create receiver (async)
            self.receiver = ServerReceiver(
                port=rx_port,
                input_queue=self.matching_queue,
                header_fmt=HEADER_FMT_RX,   #specific header format for RX in constructor
            )

            # Start background TCP threads
            self.sender.start()
            self.receiver.start()

            print("[PU Connector] Server started successfully.")

            # Start asynchronous receiver loop to read whenever a new frame from the embedded client has been received
            self.running = True
            self.receiver_thread = threading.Thread(
                target=self._receiver_loop,
                daemon=True
            )
            self.receiver_thread.start()

            return True

        except Exception as ex:
            print(f"[PU Connector] Connection failed: {ex}")
            return False

    # ----------------------------------------------------------
    # DISCONNECT
    # ----------------------------------------------------------
    def disconnect(self):
        print("[PU Connector] Disconnecting...")

        self.running = False

        if self.sender:
            try:
                self.sender.stop()
            except:
                print("[PU Connector] Sender stop failed")

        if self.receiver:
            try:
                self.receiver.stop()
            except:
                print("[PU Connector] Receiver stop failed")
        
        if self.receiver_thread:
            self.receiver_thread.join()
            self.receiver_thread = None

        self.sender = None
        self.receiver = None
        self.sender_queue = None
        self.matching_queue = None

        print("[PU Connector] Disconnected.")

    # ----------------------------------------------------------
    # SEND DATA FOR PREDICTION (CARLA → Sender)
    # ----------------------------------------------------------
    def sendDataForPrediction(self, img):
        """
        Called by CARLA sensor pipeline.

        Works asynchronously:
        - create metadata from image
        - Pushes dict into sender_queue
        - Actual TCP sending happens asynchronously in ServerSender.run()
        """

        if self.sender is None:
            print("[PU Connector] ERROR: Sender not running")
            return False

        #convert the image to 3 BGR channel in case it is RGBA
        #BGR -> RGB is done by the model directly
        img = self.bgra_to_bgr(img)

        #create metadata
        metadata = self.prepare_metadata(img)

        #put all together
        data = {
            "img": img,
            "metadata": metadata
        }

        # push into sender queue
        self.sender.sendDataForPrediction(data)
        return True

# ----------------------------------------------------------
    # ASYNCHRONOUS RECEIVER LOOP 
    # ----------------------------------------------------------
    def _receiver_loop(self):
        """
        Runs in background.
        Every time ServerReceiver produces a (frame, mask),
        immediately forward it to CarlaProcessorService via callback.
        """
        print("[PU Connector] Receiver loop started")

        while self.running:
            if self.receiver is None:
                time.sleep(0.05)
                continue

            result = self.receiver.receiveDataFromPrediction()

            if result is None:
                time.sleep(0.01)
                continue

            # unpack the result = input_data, output_prediction, mode
            input_data, output_prediction, mode = result

            frame_id = struct.unpack("<I", input_data["metadata"][:4])[0]
            input_image = input_data["img"]
            
            #prepare the postprocessed output based on mode, for sending back to the GUI
            if mode == ImageModality.SEGMENTATION:
                print(f"[PU Connector] Processing segmentation output for frame {frame_id}")
                output_image = self.add_mask_segmentation(input_image, output_prediction, alpha=1.0)
                
                #stack input and output vertically for visualization
                # output_image = np.vstack([input_image, output_image])

            elif mode == ImageModality.DEPTH:
                print(f"[PU Connector] Processing depth output for frame {frame_id}")
                output_image = self.visualize_scene3d(input_image, output_prediction, alpha=0.7)
            
            else:
                print(f"[PU Connector] WARNING: Unknown ImageModality {mode}, passing raw prediction")
                output_image = output_prediction

            

            # Safety: ensure CarlaProcessor exists
            if self.carlaServiceConnector is None:
                print("[PU Connector] ERROR: CarlaProcessorServiceConnector is None")
                continue

            # Call the CarlaProcessor internal callback
            try:
                # print("[PU Connector] Calling PredictionUnitReplyReceived callback")
                self.carlaServiceConnector.PredictionUnitReplyReceived(frame_id, output_image, mode)
            except Exception as e:
                print(f"[PU Connector] Error in callback: {e}")

        print("[PU Connector] Receiver loop stopped")


    def bgra_to_bgr(self, bgra_image):
        if bgra_image.ndim == 3 and bgra_image.shape[2] == 4:
            bgr_image = bgra_image[:, :, :3]
        else:
            bgr_image = bgra_image
        
        return bgr_image

    ############################
    #  utils
    ############################

    def prepare_metadata(self, image):
        """
        Prepare metadata for sending image to prediction unit.
        Metadata format: frame_id, height, width, channels, dtype, total bytes
        """
        H, W = image.shape[:2]
        C = image.shape[2] if image.ndim == 3 else 1

        # Determine dtype code
        if image.dtype == np.uint8:
            dtype = DataType.UINT8.value
        elif image.dtype == np.float32:
            dtype = DataType.FLOAT32.value
        else:
            raise ValueError("Unsupported image dtype")

        total_bytes = image.nbytes

        metadata = struct.pack(
            HEADER_FMT_TX,
            self.sender_framecounter,
            H,
            W,
            C,
            dtype,
            total_bytes,
            ImageModality.INPUT.value
        )

        print(f"[PU Connector] Prepared metadata: frame_id={self.sender_framecounter}, "
              f"size=({H}x{W}x{C}), dtype={dtype}, total_bytes={total_bytes}")

        #increment sender framecounter
        self.sender_framecounter += 1

        return metadata

    ############################
    #   VISUALIZATION utils
    ############################

    def mask_segmentation(self, prediction):
        """
        Generate RGB visualization from prediction mask.
        Background = orange, class 1 = purple, class 2 = green.
        """
        shape = prediction.shape
        vis_predict_object = np.zeros((shape[0], shape[1], 3), dtype="uint8")

    # ------------------------------------------------------
        # Light blue background (BGR)
        # ------------------------------------------------------
        vis_predict_object[:, :, :] = (255, 100, 0)

        # ------------------------------------------------------
        # Class 1 → Purple (BGR)
        # ------------------------------------------------------
        fg = np.where(prediction == 1)
        vis_predict_object[fg[0], fg[1], :] = (255, 28, 145)

        # ------------------------------------------------------
        # Class 2 → Green (BGR)
        # ------------------------------------------------------
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


    def visualize_scene3d(self, input_frame, prediction, alpha):
        """
        Create output image for scene 3d depth estimation
        Target size = prediction size
        """
        # Normalize prediction to [0, 255]
        prediction_image = 255.0 * (
            (prediction - np.min(prediction)) / (np.max(prediction) - np.min(prediction) + 1e-8)
        )
        prediction_image = prediction_image.astype(np.uint8)

        # Apply colormap → (H, W, 3)
        prediction_image = cv2.applyColorMap(prediction_image, cmapy.cmap('viridis'))

        # Resize input frame to match prediction
        if input_frame.shape[:2] != prediction_image.shape[:2]:
            input_frame = cv2.resize(input_frame, (prediction_image.shape[1], prediction_image.shape[0]))

        # Ensure input is 3 channels
        if len(input_frame.shape) == 2:
            input_frame = cv2.cvtColor(input_frame, cv2.COLOR_GRAY2BGR)

        # Blend
        output_frame = cv2.addWeighted(prediction_image, alpha, input_frame, 1 - alpha, 0)
        return output_frame
