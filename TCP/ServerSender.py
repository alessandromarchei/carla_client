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
    Server that sends images to the client asynchronously.
    Operating modes:
    1) Filesystem mode: scans a folder and sends images at fixed fps
    2) Async queue mode: waits for external modules to push images into input_queue (trhough the sendDataForPrediction() function)

    External interface:
        sendDataForPrediction(img, frame_id)
            --> pushes (img, frame_id) into input_queue
            --> does NOT send immediately

    Internal thread:
        run()
          --> waits for items in input_queue
            --> calls _send_frame() to send metadata+payload
    """

    def __init__(self, port, input_queue: BlockingQueue, sent_queue: BlockingQueue,
                input_folder: str | None = None, fps: float | None = 10.0):
        super().__init__(port)

        self.input_queue = input_queue
        self.sent_queue = sent_queue
        self.input_folder = input_folder
        self.frameIDcounter = 0

        #fps count only if we have a folder to scan, otherwise it depends on the senddataforprediction
        if input_folder is None :
            self.fps = None
        else:
            self.fps = fps

        #set operating omde based on the specified folder 
        if input_folder is not None:
            self.mode = "filesystem_mode"
        else:
            self.mode = "async_mode"

        self.default_polling_frequency = 50.0  # check the buffer is not empty every tot ms


    # -------------------------------------------
    #   PUBLIC → push frame into sending queue
    # -------------------------------------------
    def sendDataForPrediction(self, img: np.ndarray, frame_id: int | None):
        """
        Called by the CARLA pipeline.
        DOES NOT SEND the image.
        Only enqueues (img, frame_id) for asynchronous sending.
        """
        if frame_id is None:
            self.frameIDcounter += 1
            frame_id = self.frameIDcounter

        self.input_queue.push({"img": img, "frame_id": frame_id})


    # -------------------------------------------
    #   INTERNAL → 
    # -------------------------------------------
    def _send_frame(self, img: np.ndarray, frame_id: int):
        if not self.running:
            print("[ServerSender] ERROR: Server not running.")
            return False

        if self.client_sock is None:
            print("[ServerSender] ERROR: No client connected.")
            return False

        if img is None:
            print("[ServerSender] ERROR: img is None.")
            return False

        #prepare metadata
        img = np.ascontiguousarray(cv2.resize(img, (640, 320)))
        H_image, W_image = img.shape[:2]
        C_image = 1 if img.ndim == 2 else img.shape[2]
        raw = img.tobytes()

        #pack the metadata into a struct
        metadata = struct.pack(METADATA_FMT, frame_id, H_image, W_image, C_image)

        #send metadata nad the frame
        try:
            self.client_sock.sendall(metadata)
            self.client_sock.sendall(raw)
        except Exception as e:
            print(f"[ServerSender] ERROR during send: {e}")
            self.stop()
            return False

        # put the sent data inside the queue, used by the receiver after
        if self.sent_queue is not None:
            self.sent_queue.push({
                "frame_id": frame_id,
                "img": img,
                "H": H_image,
                "W": W_image,
                "C": C_image,
                "timestamp": time.time(),
            })

        print(f"[ServerSender] SENT frame {frame_id} ({H_image}x{W_image}x{C_image}, {len(raw)} bytes)")
        return True


    # -------------------------------------------
    #   THREAD LOOP: async sending
    # -------------------------------------------
    def run(self):

        #start server : waits until someone connects (BLOCKING)
        if not self.startServer():
            print("[ServerSender] Failed to start")
            return

        print(f"[ServerSender] Started async sender (fps={self.fps})")

        #calculat time to wait between each image to send if we have a valid fps value
        if self.fps is not None and self.fps > 0:
            frame_interval = 1.0 / self.fps if self.fps > 0 else 0
        else :
            frame_interval = None

        # ---- Option 1: load from folder in background ----
        if self.mode == "filesystem_mode":
            folder = os.path.expanduser(self.input_folder)
            imgs = sorted(os.listdir(folder))

            for fname in imgs:
                if not self.running:
                    break
                path = os.path.join(folder, fname)
                img = cv2.imread(path)
                if img is None:
                    continue

                self.frameIDcounter += 1
                self._send_frame(img, self.frameIDcounter)
                time.sleep(frame_interval)

            self.sent_queue.stop()
            return

        elif self.mode == "async_mode":
            # ---- : pure async queue sending ----
            while self.running:
                item = self.input_queue.pop(timeout=0.1)
                if item is None:
                    continue

                img = item["img"]
                frame_id = item["frame_id"]

                self._send_frame(img, frame_id)

                if self.default_polling_frequency > 0:
                    time.sleep(1.0 / self.default_polling_frequency)

        self.sent_queue.stop()
