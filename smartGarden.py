import RPi.GPIO as GPIO
import keyboard
import threading
from datetime import datetime
from datetime import timedelta
import time
import os
import zipfile
import logging
import GardenModules.soilMoisture.soil as soil
import GardenModules.sunlightSensor.sunlight as sunlight
import GardenModules.email.email as email



#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
WAIT_TIME_SECONDS = 600
EMAIL_TIME_SECONDS = 14400
PUMP_TIME_SECONDS = 10800
CAMERA_TIME_SECONDS = 300
ARTIFICIAL_LIGHT_SECONDS = 1800
LAMP_PIN = 16
image_count = 0

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
	logging.info("zipping path: " + path)
	for root, dirs, files in os.walk(path):
		logging.info("root: " + root)
		for file in files:
			ziph.write(os.path.join(root, file))

def send_folder(ymd):
	time1 = datetime.now()
	logging.info("Zipping File... "+ str(datetime.now()))
	baseFolder = ymd
	ymd = baseFolder + ".zip"
	currentDirectory = os.path.dirname(os.path.realpath(__file__))
	os.chdir("/home/pi/Desktop/smartGarden/smartGarden/images")
	zf = zipfile.ZipFile(ymd, mode = 'w', compression=zipfile.ZIP_LZMA)
	try:
		zipdir(baseFolder,zf)
	finally:
		zf.close()
	logging.info("Sending images...")
	try:
		scp_command = "SSHPASS='al.EX.91.27' sshpass -e scp " + ymd + " alext@192.168.0.20:D:\\\\smartGarden\\\\Images"
	except Exception as e:
		logging.warn("There was an error sending the file to Cacutar")
		logging.warn(e)
	try:
		os.system(scp_command)
		os.system("rm " + ymd)
		os.system("rm -r " + baseFolder)
		os.chdir(currentDirectory)
		time2 = datetime.now()
		diff = time2 - time1
		logging.info("It took (mins, seconds): " + str(divmod(diff.total_seconds(),60)) + " to transfer " + str(ymd))
	except Exception as e:
		logging.warn("There was an error deleting the folders and moving back a directory")
		logging.warn(e)

def take_pics(ymd, number=1):
	for x in range(number):
		logging.info("Taking image " + str(x + 1) + " out of " + str(number))
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
		yesterday = datetime.now() - timedelta(days=1)
		filename = str(yesterday).replace(" ", "-")
		dateArray = filename.split('-')
		ymd = dateArray[0] + "-" + dateArray[1] + "-" + dateArray[2]
		send_folder(ymd)
		ymd = create_folder()
	take_pics(ymd)

def run_pump(run_time):
	try:
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
		logging.info("Watered plants at: " + str(datetime.now()))
	except Exception as e:
		logging.warn("There was an error watering the plants.")
		logging.warn(e)

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
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> Soil Moisture </th>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> TimeStamp </th>
						</tr>
						"""
		soilLogArray = []
		with open("/home/pi/Desktop/smartGarden/smartGarden/soilLog.txt", "r") as fp2:
			for count, line in enumerate(fp2):
				soilLogArray.append(line)

		with open("/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt", "r") as fp:
			for cnt, line in enumerate(fp):
				lineArray = line.split()
				currentYMD = str(datetime.now()).split()[0]
				soilMoisture = "No Data"
				soilTimeStamp = "No Data"
				highlightedRow = "<td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>"
				regularRow = "<td style='border: 1px solid;padding: 8px; text-align: center;'>"
				greyRow = "<td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center'>"
			
				if cnt < len(soilLogArray):
						try:
								splitLine = soilLogArray[cnt].split()
								soilMoisture = splitLine[3]
								soilTimeStamp = splitLine[4] + " " + splitLine[5]
						except Exception as e:
								logging.warn("Unable to parse soil moisture or time stamp for email.")
								logging.warn(e)

				if currentYMD == lineArray[3]:
						if cnt % 2 == 0:
								if "YES" in lineArray[0]:
										row = "<tr>" + highlightedRow  + lineArray[0] + " " + lineArray[1] + "</td>"
								else:
										row = "<tr>" + regularRow + lineArray[0] + " " + lineArray[1] + "</td>"

								row = row + regularRow + lineArray[3] + " " +  lineArray[4]+ "</td>"
								row = row + regularRow + soilMoisture + "</td>"
								row = row + regularRow + soilTimeStamp + "</td></tr>"
						else:
								if "YES" in lineArray[0]:
										row = "<tr>" + highlightedRow + lineArray[0] + " " + lineArray[1] + "</td>"
								else:
										row = "<tr>" + greyRow + lineArray[0] + " " + lineArray[1] + "</td>"
								row = row + greyRow + lineArray[3] + " " +	lineArray[4]+ "</td>"
								row = row + greyRow + soilMoisture + "</td>"
								row = row + greyRow + soilTimeStamp + "</td></tr>"
						html = html + row
				elif currentYMD == lineArray[4]:
						if cnt % 2 == 0:
								if "YES" in lineArray[0]:
										row = "<tr>" + highlightedRow + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
								else:
										row = "<tr>" + regularRow + lineArray[0] + " " + lineArray[1] + "</td>"
								row = row + regularRow + lineArray[4] + " " +  lineArray[5]+ "</td>"
								row = row + regularRow + soilMoisture + "</td>"
								row = row + regularRow + soilTimeStamp + "</td></tr>"
						else:
								if "YES" in lineArray[0]:
										row = "<tr>" + highlightedRow + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
								else:
										row = "<tr>" + greyRow + lineArray[0] + " " + lineArray[1] + "</td>"
								row = row + greyRow + lineArray[4] + " " +	lineArray[5]+ "</td>"
								row = row + greyRow + soilMoisture + "</td>"
								row = row + greyRow + soilTimeStamp + "</td></tr>"
						html = html + row
				html = html + """\
						</table>
					</body>
				</html>
				"""
	except Exception as e:
		logging.warn("There was an error reading html file. Defaulting to basic html page")
		html = """\
		<html>
			<head></head>
			<body>
				<h1>Garden Update</h1>
			</body>
		</html>
		"""
		logging.warn(e)

	try:
		#Open the file to be sent
		attachment = open("/home/pi/Desktop/smartGarden/smartGarden/smartGardenLog.txt", "rb")
		p = MIMEBase('application', 'octet-stream')
		p.set_payload((attachment).read())
		encoders.encode_base64(p)

		p.add_header('Content-Disposition', "attachment; filename=%s" % "GardenLog.txt")
		message.attach(p)
	except Exception as e:
		logging.warn("There was an error opening attachment.")
		logging.warn(e)
	finally:
		attachment.close()

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
		logging.info("Email Sent "+ str(datetime.now()))

def control_artifical_light(on_off):
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(LAMP_PIN, GPIO.OUT, initial=1)
		if on_off == "on":
			GPIO.output(LAMP_PIN, 0)
		else:
			GPIO.output(LAMP_PIN, 1)
	except Exception as e:
		logging.warn(e)

def run_artificial_light():
	try:
		currentTimeStamp = str(datetime.now()).split()[1]
		currentHour = int(currentTimeStamp.split(':')[0])
		logging.info("Currrent time: " + str(currentHour))
		if currentHour >= 18 or (currentHour >= 6 and currentHour < 12):
			control_artifical_light("on")
			logging.info("Turning light on "+ str(datetime.now()))
		elif (currentHour >= 12 and currentHour < 18) or currentHour < 6:
			control_artifical_light("off")
			logging.info("Turning light off "+ str(datetime.now()))
	except Exception as e:
		logging.info("Could not setup light "+ str(datetime.now()))
		logging.warn(e)

def email_thread():
	#time.sleep(60)
	email.send_email()
	timer = threading.Event()
	while not timer.wait(EMAIL_TIME_SECONDS):
		email.send_email()

def sunlight_thread():
	sunlight.check_sunlight()
	timer = threading.Event()
	while not timer.wait(WAIT_TIME_SECONDS):
		sunlight.check_sunlight()

def pump_thread():
	timer = threading.Event()
	while not timer.wait(PUMP_TIME_SECONDS):
		run_pump(5)

def camera_thread():
	ymd = create_folder()
	run_camera(ymd)
	timer = threading.Event()
	while not timer.wait(CAMERA_TIME_SECONDS):
		run_camera(ymd)

def artifical_light_thread():
	run_artificial_light()
	timer = threading.Event()
	while not timer.wait(ARTIFICIAL_LIGHT_SECONDS):
		run_artificial_light()
	GPIO.cleanup()

def soil_moisture_thread():
	soil.check_soil()
	timer = threading.Event()
	while not timer.wait(WAIT_TIME_SECONDS):
		soil.check_soil()
	


if __name__ == "__main__":
	logging.basicConfig(filename="/home/pi/Desktop/smartGarden/smartGarden/smartGardenLog.txt", level=logging.INFO)
	thread1 = threading.Thread(target=email_thread)
	thread2 = threading.Thread(target=sunlight_thread)
	thread3 = threading.Thread(target=pump_thread)
	thread4 = threading.Thread(target=camera_thread)
	thread5 = threading.Thread(target=artifical_light_thread)
	thread6 = threading.Thread(target=soil_moisture_thread)

	thread1.start()
	thread2.start()
	thread3.start()
	thread4.start()
	thread5.start()
	thread6.start()
	thread1.join()
	thread2.join()
	thread3.join()
	thread4.join()
	thread5.join()
	thread6.join()
