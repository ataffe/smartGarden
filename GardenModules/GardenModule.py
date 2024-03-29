from threading import Thread


class GardenModule(Thread):
	def __init__(self, queue):
		super().__init__()
		self._sentinel = queue
		self.daemon = True
		self._startup = True

	def is_running(self):
		return self._startup

	def run(self):
		pass

	def shutdown(self):
		print("Sentinel triggered in garden module.")
		self._sentinel.get(block=True)
		self._sentinel.put(True)
		self._sentinel.task_done()

	def health_check(self):
		return "ok"
