# TCP/ServerBase.py

import socket
import threading


class ServerBase:
    def __init__(self, port):
        self.port = port
        self.sock = None          # listening socket
        self.client_sock = None   # connected client
        self.running = False
        self.worker = None

        self.name = "[ServerBase]"

    def _reset_client(self):
        """Close the current client and reset it."""
        if self.client_sock:
            try:
                self.client_sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self.client_sock.close()
            except:
                pass
        self.client_sock = None

    def acceptClient(self):
        """
        Try to accept a client.
        It is NOT blocking forever: if it fails, it returns False.
        """
        try:
            self.client_sock, addr = self.sock.accept()
            print(f"{self.name} Client connected on port {self.port} from {addr}")
            return True
        except Exception as e:
            print(f"{self.name} accept error on port {self.port}: {e}")
            return False

    # ------------------------------------------
    # startServer() — bind & listen only once
    # ------------------------------------------
    def startServer(self):
        """
        Create the listening socket.
        Does NOT call accept: that is done by acceptClient() inside run().
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.listen(1)
        except Exception as e:
            print(f"{self.name} bind/listen error on port {self.port}: {e}")
            return False

        print(f"{self.name} Listening on port {self.port}...")
        return True

    # ------------------------------------------
    # start() — spawn thread per run()
    # ------------------------------------------
    def start(self):
        self.running = True
        self.worker = threading.Thread(target=self.run, daemon=True)
        self.worker.start()

    def stop(self):
        print(f"{self.name} Stopping base server on port {self.port}...")
        self.running = False

        # reset client
        self._reset_client()

        # close server socket
        try:
            if self.sock:
                self.sock.close()
        except:
            pass

        # join thread
        if self.worker and self.worker.is_alive():
            self.worker.join()

    # virtual only here
    def run(self):
        raise NotImplementedError
