import RPi.GPIO as GPIO
import time

LAMP_PIN = 16
try:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LAMP_PIN, GPIO.OUT, initial=1)
	GPIO.output(LAMP_PIN, 0)
	time.sleep(5)
	GPIO.output(LAMP_PIN, 1)
except Exception as e:
	print(e)
finally:
	GPIO.cleanup()
