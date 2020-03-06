from threading import Thread


class GardenModule(Thread):
	def __init__(self):
		super().__init__()
		self._shutDownFlag = False
		self.daemon = True

	def run(self):
		pass

	def shutdown(self):
		self._shutDownFlag = True
