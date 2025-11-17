from .ServerBase import ServerBase
import cv2
import os
import time
import numpy as np

class ServerSender(ServerBase):
    def __init__(self, port, folder, out_queue, fps=10.0):
        super().__init__(port)
        self.folder = folder
        self.out_queue = out_queue
        self.fps = fps

    def send_image(self, img):
        """
        Send a numpy uint8 image (H,W,3) to the client.
        Exactly equivalent to C++ send(client_fd_, resized.data, img_size, 0)
        """

        if not self.running:
            print("[ServerSender] ERROR: Server not running, cannot send.")
            return False

        if self.client_socket is None:
            print("[ServerSender] ERROR: No client connected.")
            return False

        # Ensure contiguous raw buffer
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)

        raw = img.tobytes()
        size = len(raw)

        try:
            self.client_socket.sendall(raw)
            print(f"[ServerSender] Sent image ({size} bytes)")
            return True
        except Exception as e:
            print(f"[ServerSender] send_image() failed: {e}")
            self.stop()
            return False



    def run(self):
        if not self.startServer():
            print("[ServerSender] Failed to start")
            return

        # Scan directory
        images = sorted(
            [os.path.join(self.folder, f) for f in os.listdir(self.folder)
             if os.path.isfile(os.path.join(self.folder, f))]
        )

        if not images:
            print("[ServerSender] No images found.")
            self.running = False
            return

        print(f"[ServerSender] Loaded {len(images)} images.")
        print(f"[ServerSender] Starting transmission at {self.fps} FPS")

        frame_interval = 1.0 / self.fps if self.fps > 0 else 0

        for path in images:
            if not self.running:
                break

            img = cv2.imread(path)
            if img is None:
                print("[ServerSender] Skipping unreadable", path)
                continue

            resized = cv2.resize(img, (640, 320), interpolation=cv2.INTER_AREA)
            data = resized.tobytes()

            try:
                self.client_sock.sendall(data)
            except Exception as e:
                print("[ServerSender] send failed:", e)
                break

            print(f"[ServerSender] Sent {os.path.basename(path)} ({len(data)} bytes)")

            self.out_queue.push({
                "img": resized,
                "timestamp": time.time()
            })

            if frame_interval > 0:
                time.sleep(frame_interval)

        self.out_queue.stop()
        self.running = False
