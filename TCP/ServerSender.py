# TCP/ServerSender.py

from .ServerBase import ServerBase, print_metadata_py
from .Buffer import BlockingQueue
import cv2
import os
import time
import numpy as np
import struct

class ServerSender(ServerBase):
    """
    TCP sender (TX). It continuously sends data to the client, running the AI models
    - receives data dicts from input_queue, through sendDataForPrediction()
    - Sends (metadata, payload)
    - puts sent data into sent_queue for matching (used from the serverreceiver)
    """

    def __init__(self, port, input_queue: BlockingQueue, sent_queue: BlockingQueue):
        super().__init__(port)

        self.input_queue = input_queue
        self.sent_queue = sent_queue

        self.name = "[Sender]"

        self.default_polling_frequency = 50.0  # Hz queue polling

    # -------------------------------------------------------
    # Push data into the internal buffer queue (called from PredictionServerConnector)
    # -------------------------------------------------------
    def sendDataForPrediction(self, data: dict):
        #receives a dict containing "img" and "metadata"

        if "img" not in data or "metadata" not in data:
            print(f"{self.name} ERROR: data dict must contain 'img' and 'metadata' keys.")
            return False

        print(f"{self.name} Enqueuing frame {struct.unpack('!I', data['metadata'][:4])[0]} for sending.")
        #push new data dict into the queue
        self.input_queue.push(data)

    # -------------------------------------------------------
    # INTERNAL :send one frame to the client
    # -------------------------------------------------------
    def _send_data(self, data: dict):
        if not self.running:
            print(f"{self.name} ERROR: Server not running.")
            return False

        if self.client_sock is None:
            print(f"{self.name} WARNING: No client connected — dropping frame.")
            return False

        if data is None or "img" not in data or "metadata" not in data:
            print(f"{self.name} ERROR: img is None.")
            return False

        # extract data from dict
        img = data["img"]
        metadata = data["metadata"]

        #ensure image is stored contiguously
        img = np.ascontiguousarray(cv2.resize(img, (640, 320)))
        
        #convert image to raw bytes
        raw_image = img.tobytes()

        # print_metadata_py(metadata, "SERVER SENDING METADATA (TO CLIENT)")

        try:
            self.client_sock.sendall(metadata)
            self.client_sock.sendall(raw_image)

        except Exception as e:
            print(f"{self.name} ERROR during send: {e}")
            self._reset_client()   # immediately drop dead client
            return False

        # Store sent data for matching
        if self.sent_queue is not None:
            self.sent_queue.push({"metadata": metadata, "img": img})

        print(f"{self.name} SENT frame {metadata[0]} "
              f"({metadata[1]}x{metadata[2]}x{metadata[3]}, {len(raw_image)} bytes)")
        return True

    # -------------------------------------------------------
    # THREAD LOOP → async sending + auto-reconnect
    # -------------------------------------------------------
    def run(self):

        # Start server: bind + listen (non-blocking accept)
        if not self.startServer():
            print(f"{self.name} Failed to start")
            return

    
        # -------------------------------------------------------
        # ASYNC STREAMING, run continously
        # -------------------------------------------------------
        while self.running:

            # No client → try to accept one
            if self.client_sock is None:
                self.acceptClient()
                time.sleep(0.05)
                continue

            # Consume item from the input queue, if data is avalable from the carla simulator
            item = self.input_queue.pop(timeout=0.1)
            if item is None:
                continue
            
            #send data to the client
            self._send_data(item)

            # wait a little bit for CPU
            if self.default_polling_frequency > 0:
                time.sleep(1.0 / self.default_polling_frequency)


        if self.sent_queue is not None:
            self.sent_queue.stop()
