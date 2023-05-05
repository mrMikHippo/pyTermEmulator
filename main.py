from term import TermEmulator
from threading import Thread
from cmd_db import CmdDb

MAJORV = 0
MINORV = 1

def command_processor(cmddb):
	while True:
		cmd = cmddb.get()
		if cmd:
			print(f"You have entered: {cmd}\n> ", end='')
		if cmd == 'q':
			print("Q has reached")
			break
		if cmd == 'quit':
			print("Quit has reached")
			break



if __name__ == "__main__":
	print(f"pyTermEmulator v{MAJORV}.{MINORV} (2023)")

	cmddb = CmdDb()

	name = "TerminalEmulator"
	temu = TermEmulator(name, cmddb)

	stop_threads = False
	t1 = Thread(target=temu.run, args=(lambda : stop_threads, ))
	t2 = Thread(target=command_processor, args=(cmddb, ))

	t1.start()
	t2.start()

	try:
		t2.join()
	except KeyboardInterrupt: # Catch Ctrl+C
		print("exiting...")

	# Kill TerminalEmulator thread
	stop_threads = True
	t1.join()

	exit(0)