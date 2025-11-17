# ----------------------------------------------
# Thread-safe blocking queue 
# ----------------------------------------------
import queue

class BlockingQueue:
    def __init__(self):
        self.q = queue.Queue()
        self.stopped = False

    def push(self, item):
        if not self.stopped:
            self.q.put(item)

    def pop(self, timeout=None):
        if self.stopped:
            return None
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self.stopped = True
        # unblock any waiting get()
        try:
            self.q.get_nowait()
        except:
            pass

