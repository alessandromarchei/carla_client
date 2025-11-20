
#================================================
# ===          CARLA emulator client          ===
# ===   ------------------------------------  ===
# ===     Spawned sensor object definition    ===
#================================================

from PIL import ImageTk, Image
from cv2 import ellipse2Poly
from queue import Queue
import numpy as np
import datetime
import time
import gc

# --- https://github.com/carla-simulator/carla/discussions/4691
# --- https://www.youtube.com/channel/UCzs9P7lQCclhX5hC40LiDEA
# --- https://leaderboard.carla.org/scenarios/
# --- https://www.youtube.com/watch?v=d_lSCZ2-TwY

# --- https://www.youtube.com/@ChloeDripsInLight

# --- ss://YWVzLTI1Ni1nY206bTFIWnhFcHphcEVHQGgyOTg2ODYwLnN0cmF0b3NlcnZlci5uZXQ6ODM4OA==#Strato%20ShadowSocks
class SpawnedSensorItem(object):

    #-------------------------
    #--- Public properties ---
    #-------------------------

    # --- Sensor itself object reference
    Sensor: None

    # --- Current video frames count
    FramesCount = 1

    # --- Handler to be called
    onNewVideoFrameIsRecieved: None

    # --- Image width/height ratio
    params = 1

    # --- Previously generated video frame timestamp (client side)
    receive_image_timestamp: None

    # --- Previously generated video frame timestamp (server side)
    prev_data_timestamp: None

    # --- Is video frame currently processed flag
    is_processing = False

    # --- Currently received video frames count (to calculate average Fps)
    framesCount = 0

    # --- Total Fps sum (to calculate average Fps)
    sumFps = 0

    # --- Converted image to next displaying
    PIL_image = None

    # --- Temp array for frame conversions
    temp_array = None

    # --- Receieved frames queue
    frames_queue = None

    # --- Currently recieved frames count
    received_frames_count = 0

    # --- Application settings object reference
    app_settings = None

    # --- Sensor display index
    number = 0

    # --- Application CARLA processor service
    carlaProcessorService: None

    #-------------------------

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- sensor: Sensor itself object reference
    # --- sensorIndex: Sensor position in saved array
    # --- onNewVideoFrameIsRecieved: handler to be called
    # --- params: sensor parameters
    # --- settings: application settings
    # --- parentUuid: parent vehicle UUID
    def __init__(self, sensor, sensorIndex, onNewVideoFrameIsRecieved, 
                 params, settings, number, carlaProcessorService):

        self.Sensor = sensor
        self.SensorIndex = sensorIndex
        self.onNewVideoFrameIsRecieved = onNewVideoFrameIsRecieved
        self.params = params
        self.receive_image_timestamp = datetime.datetime.now()
        self.prev_data_timestamp = 0
        self.app_settings = settings
        self.number = number
        self.carlaProcessorService = carlaProcessorService
        self.frames_queue = Queue()

    # --- New video frame from active video cam is recieved event handler
    # --- image: received video frame
    def OnNewCarlaFrameReceived(self, image = None):

        try:

            # --- USE LARGE ENOUGH TIMEOUT IN GET 
            # --- TO AVOID STUCKING IN SYNC MODE INSIDE WI-FI
            if image is None:
                image = self.frames_queue.get(False, 
                    self.app_settings.queueGetActionTimeout)[0]

            self.framesCount = self.framesCount + 1

            timestamp = datetime.datetime.now()

            averageFps = 0
            clientFps = 0
            serverFps = 0

            if self.receive_image_timestamp is not None:

                delta = timestamp - self.receive_image_timestamp
                delay = delta.total_seconds()
                clientFps = 1 / delay
                self.sumfps = self.sumFps + clientFps
                averageFps = self.sumFps / self.framesCount
                serverDelay = image.timestamp - self.prev_data_timestamp
                if serverDelay != 0:
                    serverFps = 1 / serverDelay
                else:
                    serverFps = 999

            self.receive_image_timestamp = timestamp
            self.prev_data_timestamp = image.timestamp

            image_bytes = np.uint8(self.to_rgb_array(image.raw_data,
                image.width, image.height))

            # --- Convert recieved frame to RGB image byte array
            self.PIL_image = Image.fromarray(
                image_bytes).convert('RGB')

            #self.PIL_image.save("{}.bmp".format(self.number))

            data_copy = np.copy(image.raw_data)
            shown_image = np.reshape(data_copy, 
                (self.params.imgHeight, self.params.imgWidth, 4))

            # --- Call received video frame processing on parent GUI level
            if self.onNewVideoFrameIsRecieved is not None:
                #do nothing in HEADLESS mode
                self.onNewVideoFrameIsRecieved(self.number, 
                        self.PIL_image, shown_image, self.params, clientFps, averageFps, serverFps)

            self.received_frames_count = self.received_frames_count + 1

            del image

            # --- FIX
            # --- Recreate queue to keep memory usage in acceptable bounds 
            if self.received_frames_count >= self.app_settings.maxFramesQueueSize:
                #self.frames_queue #= Queue()
                try:
                    while True:
                        self.frames_queue.get(False)
                except Exception as e:
                    pass
                self.received_frames_count = 0
                print("---------------------------- CLEAR QUEUE: {}".format(self.SensorIndex))
                #gc.collect()

            # Entry point to send received image for processing
            if self.params.ownSensor.isFront:
                if self.carlaProcessorService.tpu_Connector is not None:
                    print("Sending frame from front sensor to TPU...")
                    self.carlaProcessorService.tpu_Connector.sendDataForPrediction(
                        np.ascontiguousarray(shown_image), 
                        self.params.imgWidth, self.params.imgHeight)

        except Exception as e:
            error = "Process new video frame error: ".format(str(e))
            print(e)

    # --- Static. Convert a CARLA raw image to a BGRA numpy array
    # --- image: image to be converted
    # --- width: image to be converted width
    # --- height: image to be converted height
    @staticmethod
    def to_bgra_array(image, width, height):
        temp_array = np.frombuffer(image, dtype=np.dtype("uint8"))
        temp_array = np.reshape(temp_array, (height, width, 4))
        return temp_array

    # --- Static. Convert a CARLA raw image to a RGB numpy array
    # --- image: image to be converted
    # --- width: image to be converted width
    # --- height: image to be converted height
    @staticmethod
    def to_rgb_array(image, width, height):
        temp_array = SpawnedSensorItem.to_bgra_array(image, width, height)
        # Convert BGRA to RGB.
        temp_array = temp_array[:, :, :3]
        temp_array = temp_array[:, :, ::-1]
        return temp_array

