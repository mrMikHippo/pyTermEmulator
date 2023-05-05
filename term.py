import termios, fcntl, sys, os

class TermEmulator:

    def __init__(self, name, cmd_db, prompt = '> '):
        self._name = name
        self._cmd_db = cmd_db
        self._prompt = prompt

    def _flush(self):
        sys.stdout.flush()

    def _moveCursorLeft(self, times = 1):
        if times:
            sys.stdout.write(f'\x1b[{times}D')

    def _moveCursorLeftFlush(self, times = 1):
        self._moveCursorLeft(times)
        sys.stdout.flush()

    def _moveCursorRight(self, times = 1):
        if times:
            sys.stdout.write(f'\x1b[{times}C')

    def _moveCursorRightFlush(self, times = 1):
        self._moveCursorRight(times)
        sys.stdout.flush()

    def _printPrompt(self):
        sys.stdout.write(self._prompt)
        sys.stdout.flush()

    def _printPromptFlush(self):
        self._printPrompt()
        sys.stdout.flush()

    def _clearLine(self):
        # sys.stdout.write('\x1b[0K') # erase from cursor to end of line
        # sys.stdout.write('\x1b[1K') # erase start of line to the cursor
        # sys.stdout.write('\x1b[2K') # erase entire line
        sys.stdout.write(f'\x1b[{len(self._prompt)+1}G')
        sys.stdout.write('\x1b[0K')

    def _clearLineFlush(self):
        self._clearLine()
        sys.stdout.flush()

    def _clearToEndOfLine(self):
        sys.stdout.write('\x1b[0K')

    def _clearToEndOfLineFlush(self):
        self._clearToEndOfLine()
        sys.stdout.flush()

    def _write(self, line):
        sys.stdout.write(line)

    def _writeFlush(self, line):
        self._write(line)
        sys.stdout.flush()


    def run(self, stop):

        print(self._name, "started")

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        self._printPrompt()

        cmd = str()
        cursor_pos = 0
        try:
            while True:
                if stop():
                    break
                try:
                    c = sys.stdin.read(1)

                    if c == '\x1b':
                        # print("Got", repr(c))
                        c = sys.stdin.read(2)
                        if c == '[A': # Up arrow pressed
                            cmd = self._cmd_db.getPrevious(cmd)
                            if cmd:
                                self._clearLine()
                                self._writeFlush(cmd)
                                cursor_pos = len(cmd)
                        elif c == '[B': # Down arrow pressed
                            cmd = self._cmd_db.getNext()
                            self._clearLine()
                            self._writeFlush(cmd)
                            cursor_pos = len(cmd)

                        elif c == '[C': # Right arrow pressed, Move cursor right
                            if cursor_pos < len(cmd):
                                cursor_pos += 1
                                self._moveCursorRightFlush()
                        elif c == '[D': # Left arrow pressed, Move cursor left
                            if cursor_pos > 0:
                                cursor_pos -= 1
                                self._moveCursorLeftFlush()
                        elif c == '[H': # Home key pressed
                            self._moveCursorLeftFlush(cursor_pos)
                            cursor_pos = 0
                        elif c == '[F': # End key pressed
                            cmd_length = len(cmd)
                            if cursor_pos < cmd_length:
                                self._moveCursorRightFlush(cmd_length - cursor_pos)
                                cursor_pos = cmd_length
                        elif c == '[1': # Ctrl+key pressed
                            c = sys.stdin.read(3)
                            if c == ';5D': # left key
                                # TODO
                                pass
                            elif c == ';5C': # right key
                                # TODO
                                pass
                        elif c == '[3': # Delete key pressed
                            c = sys.stdin.read(1) # Read ~
                            if cursor_pos < len(cmd):
                                self._clearToEndOfLine()
                                cmd = cmd[:cursor_pos] + cmd[cursor_pos+1:]
                                self._write(cmd[cursor_pos:])
                                self._moveCursorLeft(len(cmd))
                                self._moveCursorRightFlush(cursor_pos)

                    elif c == '\x7f': # Backspace
                        if cursor_pos > 0:
                            self._moveCursorLeft()
                            self._clearToEndOfLine()
                            self._write(cmd[cursor_pos:])
                            self._moveCursorLeft(len(cmd))
                            self._moveCursorRightFlush(cursor_pos)
                            cmd = cmd[:cursor_pos-1] + cmd[cursor_pos:]
                            cursor_pos -= 1
                    elif c:
                        # print("Got", repr(c))
                        if cursor_pos < len(cmd):
                            sys.stdout.write(c)
                            self._clearToEndOfLine()
                            self._write(cmd[cursor_pos:])
                            # Move terminal cursor to position
                            self._moveCursorLeftFlush(len(cmd) - cursor_pos)
                        else:
                            sys.stdout.write(c)
                            sys.stdout.flush()

                        if c == '\n':
                            self._cmd_db.update(cmd)
                            cmd = str()
                            self._printPromptFlush()
                            cursor_pos = 0
                        else:
                            cmd = cmd[:cursor_pos] + c + cmd[cursor_pos:]
                            cursor_pos += 1
                        if c == 'q':
                            self._cmd_db.update(c)
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
            print(self._name, "ended")