import RPi.GPIO as GPIO
import keyboard
import threading
import datetime
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
WAIT_TIME_SECONDS = 900
#WAIT_TIME_SECONDS = 2

def check_sunlight():
	try:
		f = open("sunlightLog.txt", "a+")
		timeStamp = time.time()
		dateTimeString = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')
		if GPIO.input(4):
			f.write("NO Sunlight at: " + dateTimeString + "\n")
			print "NO SunLight at: " + dateTimeString
		else:
			f.write("YES Sunlight at: " + dateTimeString  + "\n")
			print "YES SunLight at: " + dateTimeString
	except Exception as e:
		print "There was an error writing to file."
		print e
	finally:
		f.close()

def run_continuous():
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

timer = threading.Event()
while not timer.wait(WAIT_TIME_SECONDS):
	check_sunlight()
