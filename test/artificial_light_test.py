import RPi.GPIO as GPIO
import time
from datetime import datetime


currentTimeStamp = str(datetime.now()).split()[1]
currentHour = currentTimeStamp.split(':')[0]
print("CurrentHour: " + currentHour)
print(int(currentHour))
LAMP_PIN = 16
try:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LAMP_PIN, GPIO.OUT, initial=1)
	while True:
		GPIO.output(LAMP_PIN, 0)
	#GPIO.output(LAMP_PIN, 1)
	#time.sleep(3)
except Exception as e:
	print(e)
finally:
	GPIO.cleanup()
