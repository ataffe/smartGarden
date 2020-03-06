from threading import Thread


class GardenModule(Thread):
	def __init__(self, event):
		super().__init__()
		self._sentinel = event
		self.daemon = True

	def run(self):
		pass

	def shutdown(self):
		self._sentinel.set()
