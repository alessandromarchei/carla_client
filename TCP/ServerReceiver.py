# TCP/ServerReceiver.py

from .ServerBase import ServerBase
from .Buffer import BlockingQueue
import struct
import numpy as np
import threading

HEADER_FMT = "!IIII"  # frame_id, height, width, channels
HEADER_SIZE = struct.calcsize(HEADER_FMT)


class ServerReceiver(ServerBase):
    """
    TCP receiver
    - Receives (frame_id, H, W, C, payload)
    - Matches with original frame from sender_queue
    - Stores finished results internally
    - Provides receiveDataFromPrediction() for external modules to get results, and then flush that data
    """

    def __init__(self, port, input_queue: BlockingQueue):
        super().__init__(port)
        self.input_queue = input_queue

        # store matched results: frame_id → (frame_dict, mask)
        self.ready = {}
        self.lock = threading.Lock()

    # MSG_WAITALL equivalent
    def recvall(self, size):
        data = bytearray()
        while len(data) < size and self.running:
            packet = self.client_sock.recv(size - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def run(self):
        if not self.startServer():
            return

        while self.running:

            #Receive metadata header
            metadata = self.recvall(HEADER_SIZE)
            if not metadata:
                break

            try:
                frame_id, H, W, C = struct.unpack(HEADER_FMT, metadata)
            except:
                print("[Receiver] Header unpack error")
                break

            payload_size = H * W * C

            # Receive mask payload
            payload = self.recvall(payload_size)
            if not payload:
                break

            mask = np.frombuffer(payload, dtype=np.uint8).reshape((H, W, C))

            # Retrieve matching original frame from sender_queue
            original = None
            while self.running and original is None:
                original = self.input_queue.pop(timeout=0.1)

            if original is None:
                continue

            # Store result internally
            with self.lock:
                self.ready[frame_id] = (original, mask)

        self.running = False

    def receiveDataFromPrediction(self, frame_id=None):
        """
        If frame_id given:
            return specific (frame, mask) if available.
        Else:
            return the latest (frame, mask).
        Returned data is removed from internal storage.
        """
        with self.lock:
            if frame_id is not None:
                if frame_id in self.ready:
                    result = self.ready.pop(frame_id)
                    return result
                else:
                    return None

            # No frame_id → return latest available
            if not self.ready:
                return None

            # get max frame_id (latest)
            latest_id = max(self.ready.keys())
            return self.ready.pop(latest_id)
