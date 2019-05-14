import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
print("i2c configured")

ads = ADS.ADS1115(i2c)
ads.gain = 2/3
print("ADS configured with gain: " + str(ads.gain))

chan = AnalogIn(ads, ADS.P0)
print("Analog chan set to in")
print("chan: " + str(chan.value))
print("voltage: " + str(chan.voltage))

lowest = chan.value
highest = lowest
min = 1061
max = 14667
started = False
weight = 40
valInt = 0
while True:
	if started:
		rawVal = chan.value
		val = (rawVal - min) / (max - min)
		val = val * 100
		newValInt = round(val, 5)
		rawVal = (weight * newValInt) + ((1 - weight) * valInt)
	else:
		rawVal = chan.value
		#Normalization
		val = (rawVal - min) / (max - min)
		#Convert to a percentage
		val = val * 100
		valInt = round(val, 5)

	print("Voltage: " + str(chan.voltage) + "\t\tValue: " + str(valInt))

	if not started:
		started = True

