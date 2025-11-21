# TCP/ServerReceiver.py

from .ServerBase import ServerBase, print_metadata_py
from .Buffer import BlockingQueue
from Service.Enumerations import DataType, ImageModality, dtype_map
import struct
import numpy as np
import threading
import time


class ServerReceiver(ServerBase):
    """
    TCP receiver (robust version)
    - Receives (frame_id, H, W, C, payload)
    - Matches with original frame from sender_queue
    - Stores finished results internally
    - Provides receiveDataFromPrediction()
    """

    def __init__(self, port, input_queue: BlockingQueue, header_fmt="!IIIIIII"):
        super().__init__(port)
        self.input_queue = input_queue

        # store matched results: frame_id → (frame_dict, mask)
        self.ready = {}
        self.lock = threading.Lock()

        #overwrite the self.name
        self.name = "[Receiver]"

        self.header_fmt = header_fmt
        self.header_size = struct.calcsize(self.header_fmt)

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
            metadata = self.recvall(self.header_size)

            # Connection lost or incomplete header
            if not metadata:
                print(f"{self.name} Client disconnected.")
                self._reset_client()
                continue
            
            # print_metadata_py(metadata, "SERVER RECEIVED METADATA (FROM CLIENT)")


            try:
                # frame_id, height, width, channels, dtype, total_bytes, mode
                frame_id, H, W, C, dtype, total_bytes, mode = struct.unpack(self.header_fmt, metadata)

                dtype_enum = DataType(dtype)
                mode_enum = ImageModality(mode)

                print(f"{self.name} RECEIVING frame {frame_id} "
                      f"({H}x{W}x{C}, {dtype_enum.name}, {total_bytes} bytes, mode={mode_enum.name})")
            except:
                print(f"{self.name} Header unpack error.")
                self._reset_client()
                continue

            # ---- Receive payload ----
            payload = self.recvall(total_bytes)

            if payload is None:
                print(f"{self.name} Payload receive failed. Client disconnected?")
                self._reset_client()
                continue

            try:
                print(f"{self.name} Payload received: {len(payload)} bytes")
                np_dtype = dtype_map[dtype_enum]
                mask = np.frombuffer(payload, dtype=np_dtype).reshape((H, W, C))
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
                self.ready[frame_id] = (original, mask, mode_enum)
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
