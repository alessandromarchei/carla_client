import socket
import threading
import time
import os
import cv2
import numpy as np


class ServerBase:
    def __init__(self, port):
        self.port = port
        self.sock = None
        self.client_sock = None
        self.running = False
        self.worker = None

    # ------------------------------------------
    # startServer() — bind, listen, accept
    # ------------------------------------------
    def startServer(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen(1)
        except Exception as e:
            print(f"[ServerBase] bind/listen error on port {self.port}: {e}")
            return False

        print(f"[ServerBase] Listening on port {self.port}...")

        try:
            self.client_sock, addr = self.sock.accept()
            print(f"[ServerBase] Client connected on port {self.port} from {addr}")
        except Exception as e:
            print(f"[ServerBase] accept error: {e}")
            return False

        return True

    # ------------------------------------------
    # start() — spawn thread for run()
    # ------------------------------------------
    def start(self):
        self.running = True
        self.worker = threading.Thread(target=self.run, daemon=True)
        self.worker.start()

    # ------------------------------------------
    # stop() — EXACTLY like C++ version
    # ------------------------------------------
    def stop(self):
        print(f"[ServerBase] Stopping base server on port {self.port}...")
        self.running = False

        # Shutdown socket to unblock recv()
        if self.client_sock:
            try:
                self.client_sock.shutdown(socket.SHUT_RDWR)
            except:
                pass

        # Closing sockets
        try:
            if self.client_sock:
                self.client_sock.close()
        except:
            pass

        try:
            if self.sock:
                self.sock.close()
        except:
            pass

        # Join thread
        if self.worker and self.worker.is_alive():
            self.worker.join()

    # must be implemented by derivations
    def run(self):
        raise NotImplementedError
