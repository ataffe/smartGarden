import RPi.GPIO as GPIO
import logging
import time
import threading
from GardenModules.GardenModule import GardenModule
from datetime import datetime

# TODO try to make this a thread
class WaterPump(GardenModule):
	def __init__(self, log):
		super().__init__()
		self.logging = log
		self._dutyCycle = 60
		self._pin = 18
		self._pumpInterval = 10800

	def _run(self, runtime=None, pwm=50):
		if runtime == None:
			raise Exception("The value of run_time for the water pump was none.")
		try:
			self.logging.info("watering garden with pin:" + str(self._pin) + " and dutycycle: " + str(self._dutyCycle))
			self._setup(self._pin)
			self._togglePin(self._pin)
			p = GPIO.PWM(self._pin, pwm)
			p.start(self._dutyCycle)
			time.sleep(runtime)
			GPIO.output(self._pin, GPIO.LOW)
			p.stop()
			self.logging.info("Watered plants at: " + str(datetime.now()))
		except Exception as exception:
			self.logging.warn("There was an error watering the plants.")
			self.logging.warn(exception)
			self._printWatered()

	def thread(self):
		try:
			print("Watering plant")
			self._run(3, 50)
			timer = threading.Event()
			while not timer.wait(self._pumpInterval) and not self._shutDownFlag:
				self._run(self, 3, 50)
				if self.shutDownFlag:
					break
		except Exception as exception:
			self.logging.info("There was an exception in the pump thread: ")
			self.logging.info(exception)

	def setInterval(self, interval):
		self._pumpInterval = interval

	def getInterval(self):
		return self._pumpInterval

	def _togglePin(self, pin):
		GPIO.output(pin, GPIO.HIGH)
		GPIO.output(pin, GPIO.LOW)

	def _setup(self, pin):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT)
	
	def _printWatered(self):
		self.logging.info(""" 
											,d	
									88						  
	8b	  db	  d8 ,adPPYYba, MM88MMM ,adPPYba, 8b,dPPYba,  
	`8b	d88b	d8' ""	 `Y8   88   a8P_____88 88P'   "Y8  
	`8b  d8'`8b  d8'  ,adPPPPP88   88   8PP""""""" 88		  
	`8bd8'  `8bd8'   88,	,88   88,  "8b,   ,aa 88		  
		YP	  YP	 `"8bbdP"Y8   "Y888 `"Ybbd8"' 88  
		""")
