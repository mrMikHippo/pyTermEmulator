import termios, fcntl, sys, os

class TermEmulator:

    def __init__(self, name, cmd_db, prompt = '> '):
        self._name = name
        self._cmd_db = cmd_db
        self._prompt = prompt

    def run(self, stop):

        print(self._name, "started")

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)


        sys.stdout.write(self._prompt)
        sys.stdout.flush()

        cmd = str()
        cursor_pos = 0

        try:
            while True:
                if stop():
                    break
                try:
                    c = sys.stdin.read(1)
                    if c == '\x1b':
                        c = sys.stdin.read(2)
                        if c == '[A': # Up arrow pressed
                            pass
                        elif c == '[B': # Down arrow pressed
                            pass
                        elif c == '[C': # Right arrow pressed, Move cursor right
                            if cursor_pos < len(cmd):
                                cursor_pos += 1
                                sys.stdout.write('\033[C')
                                sys.stdout.flush()
                        elif c == '[D': # Left arrow pressed, Move cursor left
                            if cursor_pos > 0:
                                cursor_pos -= 1
                                sys.stdout.write('\033[D')
                                sys.stdout.flush()
                    elif c == '\x7f': # Backspace
                        if cursor_pos > 0:
                            cursor_pos -= 1
                            cmd = cmd[:cursor_pos] + cmd[cursor_pos+1:]
                            sys.stdout.write('\b')
                            sys.stdout.write('\033[K') # Clear to the end of line
                            sys.stdout.write(cmd[cursor_pos:])
                            # Move cursor to its position
                            for _ in range(len(cmd[cursor_pos:])):
                                sys.stdout.write('\033[D')
                            sys.stdout.flush()

                        # sys.stdout.write('\033[K') # remove from position to end of line
                    elif c:
                        # print("Got", repr(c))
                        if cursor_pos < len(cmd):
                            sys.stdout.write(c)
                            sys.stdout.write('\033[K') # Clear to the end of line
                            sys.stdout.write(cmd[cursor_pos:])
                            # Move terminal cursor to position
                            for _ in range(len(cmd[cursor_pos:])):
                                sys.stdout.write('\033[D')
                            sys.stdout.flush()
                        else:
                            sys.stdout.write(c)
                            sys.stdout.flush()

                        if c == '\n':
                            self._cmd_db.update(cmd)
                            cmd = str()
                            sys.stdout.write(self._prompt)
                            sys.stdout.flush()
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