import RPi.GPIO as GPIO
import keyboard

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#def light_callback():
#	print "Light!"

#GPIO.add_event_callback(4, light_callback)

while True:
	if GPIO.input(4):
		print "no light"
	else:
		print "light"
	try:
		if keyboard.is_pressed('q'):
			print "Exiting"
			break
		else:
			pass
	except:
		break

#print GPIO.input(4)
