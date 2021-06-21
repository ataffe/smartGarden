import RPi.GPIO as GPIO
import keyboard

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def check_sunlight():
	try:
		if not GPIO.input(4):
			print("YES SunLight")
		else:
			print("NO SunLight")
	except Exception as e:
		print("There was an error reading sunlight sensor.")
		print(e)

while True:
	check_sunlight()
	try:
		if keyboard.is_pressed('q'):
			print("\n\n\nExiting\n\n")
			break
	except Exception as e:
		break

GPIO.cleanup()
