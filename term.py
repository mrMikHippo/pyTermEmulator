import termios, fcntl, sys, os

class TermEmulator:

    def __init__(self, name, db):
        self._name = name
        self._db = db

    def run(self, stop):
        
        print(self._name, "started")

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        cmd = str()

        try:
            while True:
                if stop():
                    break
                try:
                    c = sys.stdin.read(1)
                    if c == '\x1b':
                        c = sys.stdin.read(2)
                        if c == '[A':
                            print("Up arrow pressed")
                        elif c == '[C':
                            print("Right arrow pressed")
                        elif c == '[B':
                            print("Down arrow pressed")
                        elif c == '[D':
                            print("Left arrow pressed")
                    elif c:                        
                        sys.stdout.write(c)
                        sys.stdout.flush()
                        # print("Got character", repr(c))
                        if c == '\n':
                            print("Got character", repr(c))
                            self._db.update(cmd)
                            cmd = str()
                        else:
                            cmd += c
                        if c == 'e':
                            self._db.update(c)
                except IOError: pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
            print(self._name, "ended")