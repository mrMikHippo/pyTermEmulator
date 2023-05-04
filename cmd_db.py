import threading

class CmdDb:
    def __init__(self):
        self._cmd = str()
        self._lock = threading.Lock()
    
    def update(self, line):
        with self._lock:
            self._cmd = line
    
    def get(self):
        with self._lock:
            return self._cmd