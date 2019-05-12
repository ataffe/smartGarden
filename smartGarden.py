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
import os
import sqlite3
import zipfile


#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
WAIT_TIME_SECONDS = 600
EMAIL_TIME_SECONDS = 14400
PUMP_TIME_SECONDS = 14400
CAMERA_TIME_SECONDS = 300
image_count = 0

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
		else:
			f.write("NO Sunlight at: " + dateTimeString  + "\n")
			insertSunlightRecord("No Sunlight", dateTimeString, cleanDateString)
	except Exception as e:
		print("There was an error writing to file.")
		print(e)
	finally:
		f.close()

def create_folder():
	filename = str(datetime.now()).replace(" ", "-")
	dateArray = filename.split('-')
	ymd = dateArray[0] + "-" + dateArray[1] + "-" + dateArray[2]
	try:
		os.mkdir("/home/pi/Desktop/smartGarden/smartGarden/images/" + ymd)
	except FileExistsError:
		pass
	finally:
		return ymd

def zipdir(path, ziph):
	print("zipping path: " + path)
	for root, dirs, files in os.walk(path):
		print("root: " + root)
		for file in files:
			ziph.write(os.path.join(root, file))

def send_folder(ymd):
	print("Zipping File...")
	baseFolder = ymd
	ymd = baseFolder + ".zip"
	os.chdir("images")
	zf = zipfile.ZipFile(ymd, mode = 'w', compression=zipfile.ZIP_LZMA)
	try:
		zipdir(baseFolder,zf)
	finally:
		zf.close()
	print("Sending images...")
	scp_command = "SSHPASS='al.EX.91.27' sshpass -e scp " + ymd + " alext@192.168.0.20:D:\\\\smartGarden\\\\Images"
	os.system(scp_command)
	os.system("rm " + ymd)
	os.system("rm -r " + baseFolder)
	os.chdir("..")

def take_pics(ymd, number=1):
	for x in range(number):
		print("Taking image " + str(x + 1) + " out of " + str(number))
		filename = str(datetime.now()).replace(" ", "-")
		filename = filename.replace(":","-")
		filename = filename.replace(".","-")
		filename = filename + ".jpg"
		#Take image
		myCmd = 'fswebcam -q -i 0 -r 800x600 /home/pi/Desktop/smartGarden/smartGarden/images/' + ymd + "/" + str(filename)
		os.system(myCmd)

def run_camera(ymd):
	today = str(datetime.now()).split()[0]
	if today != ymd:
		send_folder(ymd)
		ymd = create_folder()
	take_pics(ymd)

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
	text = "Garden update plan text"

	try:
		html = """\
			<!DOCTYPE html>
			<html>
				<head>
				</head>
				<body>
					<h1>Garden Update</h1>
					<table style="width:100%">
						<tr>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> Sunlight </th>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> TimeStamp </th>
						</tr>
						"""
		with open("/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt", "r") as fp:
			for cnt, line in enumerate(fp):
				lineArray = line.split()
				currentYMD = str(datetime.now()).split()[0]
				if currentYMD == lineArray[3]:
					if cnt % 2 == 0:
						if "YES" in lineArray[0]:
							row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
						else:
							row = "<tr><td style='border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
						row = row + "<td style='border: 1px solid;padding: 8px; text-align: center'>" + lineArray[3] + " " +  lineArray[4]+ "</td></tr>"
					else:
						if "YES" in lineArray[0]:
							row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
						else:
							row = "<tr><td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
						row = row + "<td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center'>" + lineArray[3] + " " +  lineArray[4]+ "</td></tr>"
					html = html + row
		html = html + """\
					</table>
				</body>
			</html>
			"""
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

	try:
		#Open the file to be sent
		attachment = open("/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt", "rb")
		p = MIMEBase('application', 'octet-stream')
		p.set_payload((attachment).read())
		encoders.encode_base64(p)

		p.add_header('Content-Disposition', "attachment; filename=%s" % "sunlightLog.txt")
		message.attach(p)
	except Exception as e:
		print("There was an error opening attachment.")
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

def camera_thread():
	ymd = create_folder()
	run_camera(ymd)
	timer = threading.Event()
	while not timer.wait(CAMERA_TIME_SECONDS):
		run_camera(ymd)

if __name__ == "__main__":
	thread1 = threading.Thread(target=email_thread)
	thread2 = threading.Thread(target=sunlight_thread)
	thread3 = threading.Thread(target=pump_thread)
	thread4 = threading.Thread(target=camera_thread)

	thread1.start()
	thread2.start()
	thread3.start()
	thread4.start()
	thread1.join()
	thread2.join()
	thread3.join()
	thread4.join()
