import threading

class CmdDb:
    def __init__(self):
        self._cmd = str()
        self._lock = threading.Lock()
        self._history = list()
        self._history_position = 0 # or m.b. current_history_position
        self._buffer = str()

    def update(self, line) -> None:
        with self._lock:
            self._cmd = line
            self._history.append(line)
            self._history_position = len(self._history)
            self._buffer = str()

    def get(self) -> str:
        with self._lock:
            cmd = self._cmd
            self._cmd = str()
            return cmd

    def getPrevious(self, cmd_to_save) -> str:
        if self._history_position == len(self._history):
            self._buffer = cmd_to_save

        if self._history_position > 0:
            self._history_position -= 1
            return self._history[self._history_position]

    def getNext(self) -> str:
        if self._history_position < len(self._history):
            self._history_position += 1
            if not self._history_position == len(self._history):
                return self._history[self._history_position]
        return self._buffer