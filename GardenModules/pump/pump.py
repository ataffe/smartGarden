import RPi.GPIO as GPIO
import time
import threading
from GardenModules.GardenModule import GardenModule
from datetime import datetime
from datetime import date


class WaterPump(GardenModule):
	def __init__(self, log, queue, soil_moisture_sensor):
		super().__init__(queue)
		self._log = log
		try:
			self._pwm = 70
			self._pin = 18
			self._pumpInterval = 3600
			self.setName("pumpThread")
			self.soilMoisture = soil_moisture_sensor
			self._log.info("Pump successfully started!")
		except Exception as exception:
			self._log.error("Pump failed to start up.")
			self._log.error(exception)
			self._startup = False

	def _run(self, runtime=None, dutyCycle=50):
		if self._startup:
			if runtime is None:
				raise Exception("The value of run_time for the water pump was none.")
			try:
				self._setup(self._pin)
				self._togglePin(self._pin)
				p = GPIO.PWM(self._pin, self._pwm)
				p.start(dutyCycle)
				time.sleep(runtime)
				GPIO.output(self._pin, GPIO.LOW)
				p.stop()
			except Exception as exception:
				self._log.warn("There was an error watering the plants.")
				self._log.warn(exception)
				self._printWatered()

	def _run_sequence(self):
		self._log.info("Watered plants at: " + str(datetime.now()))
		self._run(15, 65)
	def run(self):
		try:
			print("Starting pump thread.")
			#self._run_sequence()
			timer = threading.Event()
			water_date = date.today()
			times_watered = 0

			while not timer.wait(self._pumpInterval):
				if self._pumpInterval == 10800:
					self._pumpInterval = 3600

				# if self.soilMoisture.getSoilPercentage() < 43.50:
				# 	if times_watered < 3:
				# 		self._run_sequence()
				# 		times_watered = times_watered + 1

				if water_date.strftime("%d/%m/%Y") != date.today().strftime("%d/%m/%Y"):
					if times_watered == 0:
						self._run_sequence()
						self._pumpInterval = 10800
					times_watered = 0
					water_date = date.today()
				else:
					print("Skipping watering because soil moisture is at: {:.2f}%".format(self.soilMoisture.getSoilPercentage()))
				# TODO Refactor sentinel to be part of the while loop so that when it is triggered the loop ends.
				if self._sentinel.get(block=True):
					self._log.info("Sentinel was triggered in pump thread.")
					self._sentinel.put(True)
					self._sentinel.task_done()
					break
				self._sentinel.put(False)
				self._sentinel.task_done()
		except Exception as exception:
			self._log.info("There was an exception in the pump thread: ")
			self._log.info(exception)

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
		self._log.info(""" 
											,d	
									88						  
	8b	  db	  d8 ,adPPYYba, MM88MMM ,adPPYba, 8b,dPPYba,  
	`8b	d88b	d8' ""	 `Y8   88   a8P_____88 88P'   "Y8  
	`8b  d8'`8b  d8'  ,adPPPPP88   88   8PP""""""" 88		  
	`8bd8'  `8bd8'   88,	,88   88,  "8b,   ,aa 88		  
		YP	  YP	 `"8bbdP"Y8   "Y888 `"Ybbd8"' 88  
		""")
