import logging
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from datetime import datetime


class SoilSensor(GardenModule):
    _i2c = None
    _ads = None
    _address = None
    
    def __init__(self, devAddress=0x4a):
        try:
            self._i2c = busio.I2C(board.SCL, board.SDA)
            self._ads = ADS.ADS1115(i2c, address=devAddress)
            self._ads.gain = 1
        except Exception as exception:
            logging.warn("There was an error creating a soil sensor object")
            logging.warn(exception)
        
    def checkSoil(self):
        #Set Gain to 16 bits
		# 2/3 = 14800 - 7500 = 7300
		# 1 = (Dry) 22000 - 11000 (wet) = 11000
		# 2 = 32767 - 22500 = 10267
        _ads.gain = 1
        channel = 

def check_soil():
	rawVal = 0.0
    min = 1000.0
    max = 22000.0
    started = False
    weight = 0.40
    for x in range(50):
        if started:
            rawVal = chan.value
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

	try:
		i2c = busio.I2C(board.SCL, board.SDA)
		ads = ADS.ADS1115(i2c, address=0x4a)
		#Set Gain to 16 bits
		# 2/3 = 14800 - 7500 = 7300
		# 1 = (Dry) 22000 - 11000 (wet) = 11000
		# 2 = 32767 - 22500 = 10267

		ads.gain = 1
		chan = AnalogIn(ads, ADS.P0)
		#From claibration
		min = 1000.0
		max = 22000.0
		started = False
		weight = 0.40
		for x in range(50):
			if started:
				rawVal = chan.value
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
	except Exception as e:
		logging.warn("Error calculating soil moisture")
		logging.warn(e)
	
	try:
		f = open("/home/pi/Desktop/smartGarden/smartGarden/logs/soilLog.txt", "a+")
		f.write("Soil Moisture Level: " + str(100 - round(output)) + " " + str(datetime.now()) + " Raw Value: " + str(chan.value) + "\n")
	except Exception as e:
		logging.warn("Error writing soil moisture level")
		logging.warn(e)
	finally:
		f.close()
