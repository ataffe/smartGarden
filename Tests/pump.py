import RPi.GPIO as GPIO
import time
import keyboard

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT)

GPIO.output(18, GPIO.HIGH)
GPIO.output(18, GPIO.LOW)

dutycycle = input("Please enter the duty cycle (1 - 100): ")
#hertz = input("Please enter the frequency(): ")
p = GPIO.PWM(18,70)
p.start(float(dutycycle))

#time.sleep(4)
while True:
	try:
		pass
	except KeyboardInterrupt as e:
		print("\n\n\nExiting\n\n")
		GPIO.output(18, GPIO.LOW)
		p.stop()
		break

GPIO.cleanup()
