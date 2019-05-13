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
while True:
	val = chan.value
	if val < lowest:
		lowest = val
	if val > highest:
		highest = val

	print("Voltage: " + str(chan.voltage) + " Value: " + str(val) + "   lowest: " + str(lowest) + "   highest: " + str(highest))


