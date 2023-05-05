from threading import Thread, Event

class Test:
	def __init__(self):
		self._run_event = Event()
		self._run_event.set()
		self._t1 = Thread(target=self._run, args=(self._run_event, ))

	def run(self):
		print("Run Test")
		self._t1.start()

	def stop(self):
		self._run_event.clear()
		self._t1.join()
		print("Test successfully closed")

	def _run(self, run_event):
		print("Run Test._run")
		# try:
		while run_event.is_set():
			print("Thread run")
			time.sleep(1)
		print("End of Test._run")

def main():
	test = Test()
	test.run()
	try:
		while True:
			time.sleep(0.5)
	except KeyboardInterrupt:
		print("Exiting..")
		test.stop()
		print("[ OK ]")



if __name__ == "__main__":
	main()