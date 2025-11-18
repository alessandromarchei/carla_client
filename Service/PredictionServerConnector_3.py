from TCP.ServerSender import ServerSender
from TCP.ServerReceiver import ServerReceiver
from TCP.Buffer import BlockingQueue
import time

DEFAULT_TX_PORT = 3344
DEFAULT_RX_PORT = 3345
DEFAULT_TX_RATE = 10.0
DEFAULT_IMAGE_FOLDER = None  # We always want queue-driven mode here


class PredictionUnitConnector(object):

    def __init__(self, carlaServiceConnector=None):
        print("[PU Connector] init")
        self.carlaServiceConnector = carlaServiceConnector

        self.sender_queue = None
        self.matching_queue = None

        self.sender = None
        self.receiver = None

        self.sender_framecounter = 0

    # ----------------------------------------------------------
    # CONNECT
    # ----------------------------------------------------------
    def connect(self):
        print("[PU Connector] Connecting...")

        try:
            # Thread-safe queues
            self.sender_queue = BlockingQueue()    # frames to send
            self.matching_queue = BlockingQueue()  # original frames to be matched

            # Create sender (async)
            self.sender = ServerSender(
                port=DEFAULT_TX_PORT,
                input_queue=self.sender_queue,
                sent_queue=self.matching_queue,
                input_folder=None,  # CARLA always push frames
                fps=DEFAULT_TX_RATE,
            )

            # Create receiver (async)
            self.receiver = ServerReceiver(
                port=DEFAULT_RX_PORT,
                input_queue=self.matching_queue
            )

            # Start background TCP threads
            self.sender.start()
            self.receiver.start()

            print("[PU Connector] Connected successfully.")
            return True

        except Exception as ex:
            print(f"[PU Connector] Connection failed: {ex}")
            return False

    # ----------------------------------------------------------
    # DISCONNECT
    # ----------------------------------------------------------
    def disconnect(self):
        print("[PU Connector] Disconnecting...")

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

        self.sender = None
        self.receiver = None
        self.sender_queue = None
        self.matching_queue = None

        print("[PU Connector] Disconnected.")

    # ----------------------------------------------------------
    # SEND DATA FOR PREDICTION (CARLA → Sender)
    # ----------------------------------------------------------
    def sendDataForPrediction(self, img, imgWidth=None, imgHeight=None):
        """
        Called by CARLA sensor pipeline.

        Works asynchronously:
        - Increments frame_id
        - Pushes dict into sender_queue
        - Actual TCP sending happens asynchronously in ServerSender.run()
        """

        if self.sender is None:
            print("[PU Connector] ERROR: Sender not running")
            return False

        self.sender_framecounter += 1
        frame_id = self.sender_framecounter

        # push into sender queue
        self.sender.sendDataForPrediction(img, frame_id)
        return True

    # ----------------------------------------------------------
    # RECEIVE DATA FROM PREDICTION (Receiver → CARLA)
    # ----------------------------------------------------------
    def receiveDataFromPrediction(self, frame_id=None):
        """
        Call this function from external by CARLA code to retrieve matched results.

        - If frame_id provided -> return that pair if available
        - Else -> return latest (frame, mask) pair
        """

        if self.receiver is None:
            print("[PU Connector] ERROR: Receiver not running")
            return None

        result = self.receiver.receiveDataFromPrediction(frame_id)

        if result is None:
            return None

        frame, mask = result  # unpack the tuple into the mask and hte raw frame
        return frame, mask
