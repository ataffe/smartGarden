import logging
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime

def check_soil():
	rawVal = 0.0
	try:
		i2c = busio.I2C(board.SCL, board.SDA)
		ads = ADS.ADS1115(i2c)
		#Set Gain to 16 bits
		ads.gain = 2/3
		chan = AnalogIn(ads, ADS.P0)
		#From claibration
		min = 1061
		max = 14667
		started = False
		weight = 40
		valInt = 0
		for x in range(20):
			if started:
				rawVal = chan.value
				val = (rawVal - min) / (max - min)
				val = val * 100
				newValInt = round(val, 10)
				#Exponential filter
				rawVal = (weight * newValInt) + ((1 - weight) * valInt)
			else:
				rawVal = chan.value
				#Normalization
				val = (rawVal - min) / (max - min)
				#Convert to a percentage
				val = val * 100
				valInt = round(val, 5)

			if not started:
				started = True
		output = rawVal
		logging.info("Soil Moisture Level: " + str(100 - round(output)))
	except Exception as e:
		logging.warn("Error calculating soil moisture")
		logging.warn(e)
	
	try:
		f = open("/home/pi/Desktop/smartGarden/smartGarden/soilLog.txt", "a+")
		f.write("Soil Moisture Level: " + str(100 - round(rawVal)) + " " + str(datetime.now()) + "\n")
	except Exception as e:
		logging.warn("Error writing soil moisture level")
		logging.warn(e)
	finally:
		f.close()