import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import sys
import time
import keyboard
from queue import Queue

i2c = busio.I2C(board.SCL, board.SDA)
print("i2c configured")
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1
print("ADS configured with gain: " + str(ads.gain))
chan = AnalogIn(ads, ADS.P0)

def test_min_max():
	min_value = sys.maxsize
	max_value = -sys.maxsize
	try:
		while True:
			value = chan.value
			voltage = chan.voltage
			max_value = max([value, int(max_value)])
			min_value = min([value, int(min_value)])
			print("value: {}\nvoltage: {}\nmin: {}\nmax: {}\n".format(value,voltage, min_value, max_value))
			time.sleep(0.5)
	except KeyboardInterrupt:
		print("\nfinal min: {}\n final max: {}".format(min_value, max_value))

def test_soil_moving_avg():
	window_size = int(input("Please input the window size: "))
	sum = 0
	buffer = Queue()
	while True:
		value = chan.value
		try:
			if buffer.qsize() >= window_size:
				sum += value
				sum -= buffer.get()
				percentage = ((sum / window_size) / 21680) * 100
				print("Moisture level: {}\n percentage: {:.2f}".format(sum/window_size, percentage))
				buffer.put(value)
				time.sleep(0.2)
			else:
				buffer.put(value)
				sum += value

			if keyboard.is_pressed('q'):
				print("Exiting...")
				sys.exit()
		except Exception as e:
			print(e)
			break

def test_soil():

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

		print("Voltage: " + str(chan.voltage) + "\t\tValue: " + str(chan.value))

		if not started:
			started = True
