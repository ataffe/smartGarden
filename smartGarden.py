import RPi.GPIO as GPIO
import keyboard
import threading
from datetime import datetime  
from datetime import timedelta
import time
import smtplib, ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
from os.path import basename
import sqlite3

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
WAIT_TIME_SECONDS = 600
EMAIL_TIME_SECONDS = 7200
PUMP_TIME_SECONDS = 18000

def insertSunlightRecord(message,time1, time2):
	insert_command = "INSERT INTO sunlight VALUES (\'" + message + "\',\'"+ time1 + "\',\'" + time2 + "\');"
	try:
		conn = sqlite3.connect('/home/pi/Desktop/smartGarden/smartGarden/gardenDatabase.db')
		cursor = conn.cursor()
		cursor.execute(insert_command)
		conn.commit()
		print("Inserted sunlight record")
		return cursor.lastrowid
	except Exception as e:
		print(e)
	finally:
		conn.close()

def check_sunlight():
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		f = open("/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt", "a+")
		time = datetime.now()
		dateTimeString = str(time)
		cleanDateString = str(time + timedelta(days=60))
		if not GPIO.input(4):
			f.write("YES Sunlight at: " + dateTimeString + "\n")
			insertSunlightRecord("Yes Sunlight",dateTimeString,cleanDateString)	
			print("YES SunLight at: " + dateTimeString)
		else:
			f.write("NO Sunlight at: " + dateTimeString  + "\n")
			insertSunlightRecord("No Sunlight", dateTimeString, cleanDateString)	
			print("NO SunLight at: " + dateTimeString)
	except Exception as e:
		print("There was an error writing to file.")
		print(e)
	finally:
		f.close()

def run_continuous():
	while True:
		if GPIO.input(4):
			print("no light")
		else:
			print("light")
		try:
			if keyboard.is_pressed('q'):
				print("Exiting")
				break
			else:
				pass
		except:
			break

def run_pump(run_time):
	dutycycle = 60
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.OUT)
	GPIO.output(18, GPIO.HIGH)
	GPIO.output(18, GPIO.LOW)
	p = GPIO.PWM(18,50)
	p.start(dutycycle)
	time.sleep(run_time)
	GPIO.output(18, GPIO.LOW)
	p.stop()
	GPIO.cleanup()

def send_email():
	port = 465 # For SSL
	password = "al.EX.91.27"
	sender_email = "raspberry.pi.taffe@gmail.com"
	receiver_email = "taffeAlexander@gmail.com"
	message = MIMEMultipart("alternative")
	message["Subject"] = "Garden update: " + formatdate(localtime=True)
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Date"] = formatdate(localtime=True)

	# Create the body of the message (a plain-text and an HTML version).
	text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"

	try:
		f=open("/home/pi/Desktop/smartGarden/smartGarden/email.html", "r")
		if f.mode == 'r':
				html = f.read()
		f.close()

		#Open the file to be sent
		attachment = open("/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt", "rb")
		p = MIMEBase('application', 'octet-stream')
		p.set_payload((attachment).read())
		encoders.encode_base64(p)

		p.add_header('Content-Disposition', "attachment; filename=%s" % "sunlightLog.txt")
		message.attach(p)
	except Exception as e:
		print("There was an error reading html file. Defaulting to basic html page")
		html = """\
		<html>
			<head></head>
			<body>
				<h1>Garden Update</h1>
			</body>
		</html>
		"""
		print(e)

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	message.attach(part1)
	message.attach(part2)

	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port) as server:
		server.login("raspberry.pi.taffe@gmail.com", password)
		server.sendmail(sender_email, receiver_email, message.as_string())
		print("Email Sent")

def email_thread():
	time.sleep(60)
	send_email()
	timer = threading.Event()
	while not timer.wait(EMAIL_TIME_SECONDS):
		send_email()

def sunlight_thread():
	timer = threading.Event()
	while not timer.wait(WAIT_TIME_SECONDS):
		check_sunlight()

def pump_thread():
	#run_pump(5)
	timer = threading.Event()
	while not timer.wait(PUMP_TIME_SECONDS):
		run_pump(5)

if __name__ == "__main__":
	thread1 = threading.Thread(target=email_thread)
	thread2 = threading.Thread(target=sunlight_thread)
	thread3 = threading.Thread(target=pump_thread)

	thread1.start()
	thread2.start()
	thread3.start()
	thread1.join()
	thread2.join()
	thread3.join()
