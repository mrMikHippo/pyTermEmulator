# import sys
# str = ""
# while True:
#     c = sys.stdin.read(1) # reads one byte at a time, similar to getchar()
#     if c == ' ':
#         break
#     str += c
# print(str)

import sys
import select
import tty
import termios

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)
try:
    tty.setcbreak(sys.stdin.fileno())

    # i = 0
    while True:
        # print(i)
        # i += 1

        if isData():
            c = sys.stdin.read(1)
            if c == '\x1b':         # x1b is ESC
                break
            elif c == 'q':
                print(c)
                break
            else:
                print(c)
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)