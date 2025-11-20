# TCP/ServerSender.py

from .ServerBase import ServerBase
from .Buffer import BlockingQueue
import cv2
import os
import time
import numpy as np
import struct

METADATA_FMT = "!IIII"  # frame_id, height, width, channels
METADATA_SIZE = struct.calcsize(METADATA_FMT)


class ServerSender(ServerBase):
    """
    Robust TCP async sender with automatic reconnect.

    Modes:
    1) Filesystem mode: stream files at fixed fps
    2) Async queue mode: send frames pushed by external modules

    Features:
    - Non-blocking on startup (does NOT wait for client)
    - Auto-reconnect if client disconnects
    - Keeps running even without client
    - Sender never dies on socket errors
    """

    def __init__(self, port, input_queue: BlockingQueue, sent_queue: BlockingQueue,
                 input_folder: str | None = None, fps: float | None = 10.0):
        super().__init__(port)

        self.input_queue = input_queue
        self.sent_queue = sent_queue
        self.input_folder = input_folder
        self.frameIDcounter = 0

        self.name = "[Sender]"

        # FPS used only in filesystem mode
        self.fps = fps if input_folder is not None else None

        # Mode selection
        self.mode = "filesystem_mode" if input_folder is not None else "async_mode"

        self.default_polling_frequency = 50.0  # Hz queue polling

    # -------------------------------------------------------
    # PUBLIC API → enqueue frame (not sent immediately)
    # -------------------------------------------------------
    def sendDataForPrediction(self, img: np.ndarray, frame_id: int | None):
        if frame_id is None:
            self.frameIDcounter += 1
            frame_id = self.frameIDcounter

        self.input_queue.push({"img": img, "frame_id": frame_id})

    # -------------------------------------------------------
    # INTERNAL → send one frame
    # -------------------------------------------------------
    def _send_frame(self, img: np.ndarray, frame_id: int):
        if not self.running:
            print(f"{self.name} ERROR: Server not running.")
            return False

        if self.client_sock is None:
            print(f"{self.name} WARNING: No client connected — dropping frame.")
            return False

        if img is None:
            print(f"{self.name} ERROR: img is None.")
            return False

        # Prepare image metadata
        img = np.ascontiguousarray(cv2.resize(img, (640, 320)))
        H_image, W_image = img.shape[:2]
        C_image = 1 if img.ndim == 2 else img.shape[2]
        raw = img.tobytes()

        metadata = struct.pack(METADATA_FMT, frame_id, H_image, W_image, C_image)

        try:
            self.client_sock.sendall(metadata)
            self.client_sock.sendall(raw)

        except Exception as e:
            print(f"{self.name} ERROR during send: {e}")
            self._reset_client()   # immediately drop dead client
            return False

        # Store sent data for matching
        if self.sent_queue is not None:
            self.sent_queue.push({
                "frame_id": frame_id,
                "img": img,
                "H": H_image,
                "W": W_image,
                "C": C_image,
                "timestamp": time.time(),
            })

        print(f"{self.name} SENT frame {frame_id} "
              f"({H_image}x{W_image}x{C_image}, {len(raw)} bytes)")
        return True

    # -------------------------------------------------------
    # THREAD LOOP → async sending + auto-reconnect
    # -------------------------------------------------------
    def run(self):

        # Start server: bind + listen (non-blocking accept)
        if not self.startServer():
            print(f"{self.name} Failed to start")
            return

        print(f"{self.name} Started async sender (mode={self.mode}, fps={self.fps})")

        # Calculate FPS interval (filesystem mode only)
        frame_interval = 1.0 / self.fps if (self.fps and self.fps > 0) else None

        # -------------------------------------------------------
        # MODE 1 : FILESYSTEM STREAMING
        # -------------------------------------------------------
        if self.mode == "filesystem_mode":

            folder = os.path.expanduser(self.input_folder)
            imgs = sorted(os.listdir(folder))
            idx = 0

            while self.running:

                # Try to accept client if missing
                if self.client_sock is None:
                    self.acceptClient()
                    time.sleep(0.05)
                    continue

                if idx >= len(imgs):
                    break

                # Load next frame
                path = os.path.join(folder, imgs[idx])
                img = cv2.imread(path)
                if img is None:
                    idx += 1
                    continue

                self.frameIDcounter += 1
                ok = self._send_frame(img, self.frameIDcounter)

                # If sending failed, retry after reconnection
                if ok:
                    idx += 1
                    if frame_interval:
                        time.sleep(frame_interval)
                else:
                    time.sleep(0.05)

            if self.sent_queue is not None:
                self.sent_queue.stop()
            return

        # -------------------------------------------------------
        # MODE 2 : PURE ASYNC STREAMING
        # -------------------------------------------------------
        while self.running:

            # No client → try to accept one
            if self.client_sock is None:
                self.acceptClient()
                time.sleep(0.05)
                continue

            # Consume queue
            item = self.input_queue.pop(timeout=0.1)
            if item is None:
                continue

            img = item["img"]
            frame_id = item["frame_id"]

            self._send_frame(img, frame_id)

            # Small throttling for CPU
            if self.default_polling_frequency > 0:
                time.sleep(1.0 / self.default_polling_frequency)

        # End of while
        if self.sent_queue is not None:
            self.sent_queue.stop()
