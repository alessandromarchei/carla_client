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
        """Chiude il client corrente e lo azzera."""
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
        Prova ad accettare un client.
        NON è bloccante per sempre: se fallisce, ritorna False.
        """
        try:
            self.client_sock, addr = self.sock.accept()
            print(f"{self.name} Client connected on port {self.port} from {addr}")
            return True
        except Exception as e:
            print(f"{self.name} accept error on port {self.port}: {e}")
            return False

    # ------------------------------------------
    # startServer() — bind & listen una sola volta
    # ------------------------------------------
    def startServer(self):
        """
        Crea il listening socket.
        NON chiama accept: quello lo fa acceptClient() dentro run().
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

        # chiudo client
        self._reset_client()

        # chiudo server socket
        try:
            if self.sock:
                self.sock.close()
        except:
            pass

        # join thread
        if self.worker and self.worker.is_alive():
            self.worker.join()

    # da implementare nelle derivate
    def run(self):
        raise NotImplementedError
