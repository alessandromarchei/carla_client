from .ServerBase import ServerBase
from .utils.visualization import add_mask_segmentation
import cv2
import numpy as np
import time

class ServerReceiver(ServerBase):
    def __init__(self, port, in_queue, visualize=False, save=False, fps=10.0):
        super().__init__(port)
        self.in_queue = in_queue
        self.visualize = visualize
        self.save = save
        self.fps = fps
        self.frame_idx = 0

        if visualize:
            cv2.namedWindow("Input Image")
            cv2.namedWindow("Segmentation Overlay")

    def stop(self):
        print("[ServerReceiver] Stopping receiver...")
        self.running = False

        if self.visualize:
            cv2.destroyAllWindows()

        super().stop()

    # ------------------------------------------
    # run()
    # ------------------------------------------
    def run(self):
        if not self.startServer():
            print("[ServerReceiver] Failed to start")
            return

        mask_size = 320 * 640

        while self.running:
            print(f"[ServerReceiver] Waiting for {mask_size} bytes...")

            # blocking receive
            try:
                data = self.recvall(mask_size)
            except:
                print("[ServerReceiver] Disconnected.")
                self.running = False
                break

            if not data:
                print("[ServerReceiver] Disconnected.")
                break

            # pair with sent frame
            sf = self.in_queue.pop(timeout=0.1)
            if sf is None:
                print("[ServerReceiver] No paired frame available, exiting.")
                break

            mask = np.frombuffer(data, dtype=np.uint8).reshape((320, 640))

            if self.visualize:
                overlay = add_mask_segmentation(sf["img"], mask, 0.5)
                cv2.imshow("Input Image", sf["img"])
                cv2.imshow("Segmentation Overlay", overlay)
                key = cv2.waitKey(int(max(1, 1000 / self.fps)))
                if key == 27:
                    self.running = False
                    break

            if self.save:
                overlay = add_mask_segmentation(sf["img"], mask, 0.5)
                combined = np.vstack((sf["img"], overlay))
                name = f"result_{self.frame_idx}.png"
                cv2.imwrite(name, combined)
                print("[ServerReceiver] Saved", name)
                self.frame_idx += 1

    # Python recv-all helper (MSG_WAITALL equivalent)
    def recvall(self, size):
        data = bytearray()
        while len(data) < size:
            if not self.running:
                return None
            try:
                packet = self.client_sock.recv(size - len(data))
            except:
                return None
            if not packet:
                return None
            data.extend(packet)
        return data