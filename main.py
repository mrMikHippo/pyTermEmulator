from term import TermEmulator
import time

MAJORV = 0
MINORV = 2

def printSomethingBig():
	print("------------------------<")
	print("What a life!")
	print("------------------------>")

def main():

	termemu = TermEmulator(verbose = True)
	print(termemu.getVersion())
	termemu.run()

	try:
		while True:
			cmd = termemu.getCommand()
			if cmd == 'q':
				break
			elif cmd == 'p':
				printSomethingBig()
			else:
				print(f"Error: Unknown command '{cmd}'")
			# print("Main thread")
			# time.sleep(0.5)
	except KeyboardInterrupt: pass
	finally:
		print("Exiting...")
		termemu.stop()
		print("Done")

if __name__ == "__main__":

	main()