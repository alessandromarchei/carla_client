
#================================================
# ===          CARLA emulator client          ===
# ===   ------------------------------------  ===
# ===     External vehicle control device     ===  
# ===         connector implementation        ===
#================================================

from TCP.ServerSender import ServerSender
from TCP.ServerReceiver import ServerReceiver
from TCP.Buffer import BlockingQueue

# --- https://stackoverflow.com/questions/53285659/how-can-i-wait-until-i-receive-data-using-a-python-socket

DEFAULT_TX_PORT = 3344
DEFAULT_RX_PORT = 3345
DEFAULT_TX_RATE = 10.0    #send images at 10 Hz
DEFAULT_IMAGE_FOLDER = "~/DEV/AI/datasets/acdc/acdc/rgb_anon_trainvaltest/rgb_anon/night/val_ref/GOPR0356/"


""""
BUFFERS
- Sender queue: receives images from CarlaProcessor sensors inside the vehicle and sends them to the PU client
- Receiver queue: receives images from the PU client and visualizes/saves them if needed

FUNCTIONING SCHEME
- sendDataForPrediction(): push new image into sender queue



"""

class PredictionUnitConnector(object):

    #----------------------------
    #--- Constants (commands) ---
    #----------------------------
    

    #-------------------------
    #--- Public properties ---
    #-------------------------
    
    # --- 
    sender_queue = None

    # --- 
    receiver_queue = None

    sender_framecounter = 0
    receiver_framecounter = 0
    
    # --- 
    sender = None

    # --- 
    receiver = None

    #-------------------------------------------
    #--- Public properties (events handlers) ---
    #-------------------------------------------

    # --- Default constructor 
    def __init__(self, carlaServiceConnector):

    # --- Connect to requested server and port
    # --- Required host address (Dns name)
    # --- Required remote port number
        print('PredictionUnitConnector init')

    def connect(self):
        try:
            # Shared thread-safe buffer
    	    self.sender_queue = BlockingQueue()
            self.receiver_queue = BlockingQueue()
    	    # Create Sender + Receiver
    	    
            self.sender = ServerSender(DEFAULT_TX_PORT, DEFAULT_IMAGE_FOLDER, self.sender_queue, DEFAULT_TX_RATE)
            self.receiver = ServerReceiver(DEFAULT_RX_PORT, self.receiver_queue, visualize=False, save=False, rate=DEFAULT_TX_RATE)
            
            self.sender.start()
            self.receiver.start()
    
            print('Successful Connection')
            return True
        
        except Exception as ex:
            print('Connection Failed: {}'.format(ex))
            return False

    # --- Disconnect from server
    def disconnect(self):
        if self.sender != None:
            try:
                self.sender.stop()
                self.sender = None
            except:
                print('Disconnection of sender Failed')
                
        if self.receiver != None:
            try:
                self.receiver.stop()
                self.receiver  = None
            except:
                print('Disconnection of receiver Failed')
                
        if self.queue != None:
            try:
                self.queue.flush()
                self.queue = None
            except:
                print('Disconnection Failed')
                
    # --- Send image to prediction calculation facade
    # data: image to be sent to process
    # imgWidth: image to be sent width
    # imgHeight: image to be sent height


    def sendDataForPrediction(self, data, imgWidth, imgHeight):
        #send data to sender queue
    	if self.sender != None:
            #increment the frame counter for the sender
    		self.sender_framecounter += 1

            #push image into the sender queue 
            self.sender_queue.push( (data, imgWidth, imgHeight, self.sender_framecounter) )
    		
            
            #self.sender.send(data, imgWidth, imgHeight, framecounter) // PUT THE IMAGE INTO SENDER QUEUE
    		#self.receiver.send(data, imgWidth, imgHeight, framecounter)
    
        # --- Send image to prediction calculation facade
    # data: image to be sent to process
    # imgWidth: image to be sent width
    # imgHeight: image to be sent height
    def receiveDataFromPrediction(self, data, mask):
        #called INSIDE the receiver run() function thread
        #data = struct containing INPUT image + frameID + metadata
        #mask = raw outpout received from the JETSON TPU client
        
        #send data to the PREDICTION UNIT GUI STREAM.
        #read from the receiver queue
        return applied_mask
