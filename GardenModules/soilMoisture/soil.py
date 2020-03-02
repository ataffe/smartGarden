import logging
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import threading
from adafruit_ads1x15.analog_in import AnalogIn
from GardenModules.GardenModule import GardenModule
from datetime import datetime

class SoilMoisture(GardenModule):
	def __init__(self):
		super().__init__(self)
		self._i2c = i2c = busio.I2C(board.SCL, board.SDA)
		self._ads = ADS.ADS1115(self._i2c, address=0x4a)
		self._ads.gail = 1
		self.channel = chan = AnalogIn(self._ads, ADS.P0)
		self.soilInterval = 600

	def _checkSoil(self):
		rawVal = 0.0
		try:
			#Set Gain to 16 bits
			# 2/3 = 14800 - 7500 = 7300
			# 1 = (Dry) 22000 - 11000 (wet) = 11000
			# 2 = 32767 - 22500 = 10267

			#From claibration
			min = 1000.0
			max = 22000.0
			started = False
			weight = 0.40
			for x in range(50):
				if started:
					rawVal = self.channel.value
					val = (rawVal - min) / (max - min)
					val = val * 100
					#Exponential filter
					filteredVal = (weight * val) + ((1 - weight) * val)
					output = filteredVal
				else:
					rawVal = chan.value
					#Normalization
					val = (rawVal - min) / (max - min)
					#Convert to a percentage
					val = val * 100
					output = val

				if not started:
					started = True
			
			logging.info("Soil Moisture Level: " + str(100 - round(output)) + " Raw Value: " + str(chan.value))
			#print("output: " + str(output))
			print("Soil Moisture Level: " + str(100 - round(output)) + "%")
		except Exception as exception:
			logging.warn("Error calculating soil moisture")
			logging.warn(exception)

		try:
			with open("/home/pi/Desktop/smartGarden/smartGarden/logs/soilLog.txt", "a+") as logFile:
				logFile.write("Soil Moisture Level: " + str(100 - round(output)) + " " + str(datetime.now()) + " Raw Value: " + str(self.channel.value) + "\n")
		except Exception as exception:
			logging.warn("Error writing soil moisture level")
			logging.warn(exception)

	def thread(self):
		self._checkSoil()
		timer = threading.Event()
		while not timer.wait(self.soilInterval) and not self.shutDownFlag:
			self._checkSoil()
			if self.shutDownFlag:
				break
	
