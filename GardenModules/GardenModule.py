class GardenModule:
	def __init__(self):
		self._shutDownFlag = False

	def thread(self):
		pass

	def shutdown(self):
		self._shutDownFlag = True