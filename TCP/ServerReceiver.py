# TCP/ServerReceiver.py

from .ServerBase import ServerBase
from .Buffer import BlockingQueue
import struct
import numpy as np
import threading
import time

HEADER_FMT = "!IIII"  # frame_id, height, width, channels
HEADER_SIZE = struct.calcsize(HEADER_FMT)


class ServerReceiver(ServerBase):
    """
    TCP receiver (robust version)
    - Receives (frame_id, H, W, C, payload)
    - Matches with original frame from sender_queue
    - Stores finished results internally
    - Provides receiveDataFromPrediction()
    """

    def __init__(self, port, input_queue: BlockingQueue):
        super().__init__(port)
        self.input_queue = input_queue

        # store matched results: frame_id → (frame_dict, mask)
        self.ready = {}
        self.lock = threading.Lock()

        #overwrite the self.name
        self.name = "[Receiver]"

    # -----------------------------------------------
    # Safe recv-all with disconnect detection
    # -----------------------------------------------
    def recvall(self, size):
        data = bytearray()

        while len(data) < size and self.running and self.client_sock:
            try:
                packet = self.client_sock.recv(size - len(data))
            except (ConnectionResetError, OSError):
                return None

            # client closed connection
            if not packet:
                return None

            data.extend(packet)

        return data


    # -----------------------------------------------
    # Main receiver thread
    # -----------------------------------------------
    def run(self):

        if not self.startServer():
            print(f"{self.name} ERROR: cannot start server")
            return

        print(f"{self.name} Server started.")

        while self.running:

            # ---- No client connected? Try accepting ----
            if self.client_sock is None:
                self.acceptClient()
                time.sleep(0.05)
                continue

            # ---- Try receive header ----
            metadata = self.recvall(HEADER_SIZE)

            # Connection lost or incomplete header
            if not metadata:
                print(f"{self.name} Client disconnected.")
                self._reset_client()
                continue

            try:
                frame_id, H, W, C = struct.unpack(HEADER_FMT, metadata)
            except:
                print(f"{self.name} Header unpack error.")
                self._reset_client()
                continue

            payload_size = H * W * C

            # ---- Receive payload ----
            payload = self.recvall(payload_size)

            if payload is None:
                print(f"{self.name} Payload receive failed. Client disconnected?")
                self._reset_client()
                continue

            try:
                mask = np.frombuffer(payload, dtype=np.uint8).reshape((H, W, C))
            except ValueError:
                print(f"{self.name} Payload reshape error.")
                self._reset_client()
                continue

            # ---- Retrieve original frame (non-blocking) ----
            original = None
            while self.running and original is None:
                original = self.input_queue.pop(timeout=0.1)

            if original is None:
                # still running but no original frame found → skip
                continue

            # ---- Store matched result ----
            with self.lock:
                self.ready[frame_id] = (original, mask)
        print(f"{self.name} Stopped.")


    # -----------------------------------------------
    # External interface: retrieve matched predictions
    # -----------------------------------------------
    def receiveDataFromPrediction(self, frame_id=None):
        """
        If frame_id given:
            return specific (frame, mask)
        Else:
            return latest available
        Returned data is REMOVED from internal storage.
        """
        with self.lock:

            if frame_id is not None:
                return self.ready.pop(frame_id, None)

            if not self.ready:
                return None

            latest_id = max(self.ready.keys())
            return self.ready.pop(latest_id)
