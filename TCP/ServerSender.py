from .ServerBase import ServerBase
import cv2
import os
import time

class ServerSender(ServerBase):
    def __init__(self, port, folder, out_queue, fps=10.0):
        super().__init__(port)
        self.folder = folder
        self.out_queue = out_queue
        self.fps = fps

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
