import RPi.GPIO as GPIO
import keyboard
import threading
import datetime
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
import smtplib, ssl
from os.path import basename


GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
WAIT_TIME_SECONDS = 600
EMAIL_WAIT_TIME = 3600
#WAIT_TIME_SECONDS = 2
logname = "/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt"

def check_sunlight():
	try:
		f = open(logname, "a+")
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

def send_email():
	timeStamp = time.time()
	dateTimeString = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')
	message = ""
	if GPIO.input(4):
			message = "No sunlight at: " + dateTimeString
		else:
			message = "Sunlight at: " + dateTimeString


	pir = MotionSensor(4)
	port = 465 # For SSL
	password = "al.EX.91.27"
	sender_email = "raspberry.pi.taffe@gmail.com"
	#receiver_email = input("Please enter the recivers email: ")
	receiver_email = "taffeAlexander@gmail.com"
	message = MIMEMultipart("alternative")
	message["Subject"] = "Hello From the Raspberry PI"
	message["From"] = sender_email
	message["To"] = COMMASPACE.join(receiver_email)
	message["Date"] = formatdate(localtime=True)
	text = message
	part1 = MIMEText(text)
	message.attach(part1)
	with open(logname, "rb") as file:
		part2 = MIMEApplication(file.read(), Name=basename(logname))
	#After file is closed.
	part2['Content-Disposition'] = 'attachment; filename="%s"' % basename(logname)
	message.attach(part2)

	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
		server.login("raspberry.pi.taffe@gmail.com", password)
		server.sendmail(sender_email, receiver_email, message.as_string())
		print("Email Sent")

def email_timer():
	timer = threading.Event()
	if not timer.wait(EMAIL_WAIT_TIME):
		send_email()

timer = threading.Event()

if __name__ == "__main__":
	thread = Thread(target = email_timer)
	thread.start()

	while not timer.wait(WAIT_TIME_SECONDS):
	check_sunlight()
	
	thread.join()
	print "Ended thread."



