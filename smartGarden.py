import RPi.GPIO as GPIO
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
import GardenModules.pump.pump as pump
import GardenModules.prune.prune as prune
import cv2
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_debug import Debug
import sys

# Disable logging for api
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Constants
WAIT_TIME_SECONDS = 600
EMAIL_TIME_SECONDS = 36000
PUMP_TIME_SECONDS = 10800
CAMERA_TIME_SECONDS = 300
ARTIFICIAL_LIGHT_SECONDS = 300
WAIT_TIME_PRUNE = 86400
LAMP_PIN = 16
image_count = 0
SHUTDOWN_FLAG = False
LIGHT_START_TIME = 18
LIGHT_END_TIME = 22


app = Flask(__name__, template_folder='/home/pi/Desktop/smartGarden/smartGarden/ControlPanel', static_folder="/home/pi/Desktop/smartGarden/smartGarden/ControlPanel")
CORS(app)
Debug(app)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown')
def shutdown():
	logging.info("Shutting down garden.")
	print("Shutting down garden.")
	SHUTDOWN_FLAG = True
	shutdown_server()
	return "Shutting down..."

@app.route('/heartBeat')
def heartBeat():
	return "ok"

@app.route('/setWater/<value>')
def setWater(value):
	global PUMP_TIME_SECONDS
	PUMP_TIME_SECONDS = int(value) * 3600
	print("Pump interval now set to: " + str(PUMP_TIME_SECONDS))
	return "ok"

@app.route('/getWater')
def getWater():
	try:
		print("Returning pump time: " + str(PUMP_TIME_SECONDS))
		return str(PUMP_TIME_SECONDS / 3600)
	except Exception as e:
		print(e)

@app.route('/setLight/<value>')
def setLight(value):
	global LIGHT_START_TIME
	global LIGHT_END_TIME
	LIGHT_START_TIME = int(value.split(':')[0])
	LIGHT_END_TIME = int(value.split(':')[1])
	print("Setting new start time as: " + str(LIGHT_START_TIME) + " and end time as: " + str(LIGHT_END_TIME))
	return "ok"

@app.route('/getLightTimes')
def getLight():
	try:
		print("Returning light times start: " + str(LIGHT_START_TIME) + " light times end: " + str(LIGHT_END_TIME))
		return str(LIGHT_START_TIME) + ":" + str(LIGHT_END_TIME)
	except Exception as e:
		print(e)

@app.route('/soil')
def soil_route():
	try:
		with open("/home/pi/Desktop/smartGarden/smartGarden/logs/soilLog.txt") as file:
			#lines = file.readlines()
			table = ""
			for count, line in reversed(list(enumerate(file))):
				fields = line.split()
				raw_value = fields[8]
				percent = fields[3]
				date = fields[4]
				time = fields[5]

				if count % 2 == 0:
					table = table + "<tr style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center'>"
				else:
					table = table + "<tr style='border: 1px solid;padding: 8px; text-align: center;'>"

				table = table + "<td>" + date + "</td>"
				table = table + "<td>" + time + "</td>"
				table = table + "<td>" + percent + "</td>"
				table = table + "<td>" + raw_value + "</td>"
				table = table + "</tr>"
		return '''
		<html>
			<head>
				<title>Soil Moisture - Smart Garden</title>
			</head>
			<body>
				<h1 style="font-family: 'Roboto', sans-serif;">Soil Moisture Data</h1>
				<table style="width:100%">
					<tr>
						<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;">Date</th>
						<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;">Time</th>
						<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;">Soil Moisture Percent</th>
						<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;">Soil Moisture Raw Value</th>
					</tr>
					''' + table + '''
				</table>
			</body>
		</html>
		'''
	except Exception as e:
		logging.warn("There was an exception returning soil data to rest endpoint: " + str(e))
		return "There was an exception: " + str(e)


@app.route('/garden')
def garden_route():
	with open("/home/pi/Desktop/smartGarden/smartGarden/logs/smartGardenLog.txt") as file:
		return file.read()


# Control Panel End Points
@app.route('/')
@app.route('/controlPanel')
def control_panel():
	return render_template("index.html")

@app.route('/water')
def control_panel_water():
	with open('/home/pi/Desktop/smartGarden/smartGarden/ControlPanel/water.html') as file:
		return file.read()

@app.route('/light')
def control_panel_light():
	with open('/home/pi/Desktop/smartGarden/smartGarden/ControlPanel/light.html') as file:
		return file.read()

@app.route('/soilMoisture')
def control_panel_soil_moisture():
	with open('/home/pi/Desktop/smartGarden/smartGarden/ControlPanel/soilMoisture.html') as file:
		return file.read()

@app.route('/sun_css')
def sun_css():
	with open('/home/pi/Desktop/smartGarden/smartGarden/ControlPanel/sun.css') as file:
		return file.read()

@app.route('/status_css')
def status_css():
	with open('/home/pi/Desktop/smartGarden/smartGarden/ControlPanel/status.css') as file:
		return file.read()
# End Control Panel Endpoints
			
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
	baseFolder = "/home/pi/Desktop/smartGarden/smartGarden/images/" + baseFolder
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
		#os.system("rm -r " + baseFolder)
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
		#old was 800x600
		vid_cap = cv2.VideoCapture(0)
		vid_cap.set(3, 1280)
		vid_cap.set(4, 720)
		if not vid_cap.isOpened():
			logging.warn("Error opening video device using opencv")
		else:
			print("Taking picture")
			for x in range(10):
				ret, image = vid_cap.read()
			cv2.imwrite("/home/pi/Desktop/smartGarden/smartGarden/images/" + ymd + "/" + str(filename), image)
			vid_cap.release()
			#print("Sending picture to: " + "/home/pi/Desktop/smartGarden/smartGarden/images/" + ymd + "/" + str(filename))
		#myCmd = 'fswebcam -q -i 0 -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/images/' + ymd + "/" + str(filename)
		#os.system(myCmd)

def run_camera(send_folder):
	ymd = create_folder()
	if send_folder:
		logging.info("Sending folder")
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
		if (currentHour >= LIGHT_START_TIME and currentHour < LIGHT_END_TIME):
			control_artifical_light("on")
			logging.info("Turning light on "+ str(datetime.now()))
		elif (currentHour < LIGHT_START_TIME or currentHour > LIGHT_END_TIME):
			control_artifical_light("off")
			logging.info("Turning light off "+ str(datetime.now()))
	except Exception as e:
		logging.info("Could not setup light "+ str(datetime.now()))
		logging.warn(e)
		

def email_thread():
	time.sleep(10)
	#email.send_email()
	timer = threading.Event()
	while not timer.wait(EMAIL_TIME_SECONDS) and not SHUTDOWN_FLAG:
		#email.send_email()
		if SHUTDOWN_FLAG:
			break

def sunlight_thread():
	sunlight.check_sunlight()
	timer = threading.Event()
	while not timer.wait(WAIT_TIME_SECONDS) and not SHUTDOWN_FLAG:
		sunlight.check_sunlight()
		sunlight.prune()
		if SHUTDOWN_FLAG:
			break

def pump_thread():
	#time.sleep(10)
	#pump.run_pump(8,60)
	timer = threading.Event()
	while not timer.wait(PUMP_TIME_SECONDS) and not SHUTDOWN_FLAG:
		pump.run_pump(2,40)
		pump.run_pump(3,50)
		pump.run_pump(4,60)
		if SHUTDOWN_FLAG:
			break

def camera_thread():
	#TODO ADD ANOTHER THREAD FOR SENDING IMAGES TO CACTUAR PC
	ymd = create_folder()
	timer = threading.Event()
	#run_camera(send_folder=False)
	send_folder = False
	sent_folder = False
	while not timer.wait(CAMERA_TIME_SECONDS) and not SHUTDOWN_FLAG:
		try:
			time = str(datetime.now()).split()
			hour = str(time[1].split(':')[0])
		except Exception as e:
			print("Error parsing date for camera.")
			print(e)
		if hour == "00" and not sent_folder:
			send_folder = True
			sent_folder = True
		elif hour != "00" and sent_folder:
			sent_folder = False
		else:
			send_folder = False
		run_camera(False)
		if SHUTDOWN_FLAG:
			break
		

def artifical_light_thread():
	control_artifical_light("on")
	run_artificial_light()
	timer = threading.Event()
	while not timer.wait(ARTIFICIAL_LIGHT_SECONDS) and not SHUTDOWN_FLAG:
		run_artificial_light()
		if SHUTDOWN_FLAG:
			control_artifical_light("off")
			break
	GPIO.cleanup()

def soil_moisture_thread():
	soil.check_soil()
	timer = threading.Event()
	while not timer.wait(WAIT_TIME_SECONDS) and not SHUTDOWN_FLAG:
		soil.check_soil()
		if SHUTDOWN_FLAG:
			break

def prune_logs_thread():
	prune.prune("smartGardenLog.txt")
	timer = threading.Event()
	while not timer.wait(WAIT_TIME_PRUNE) and not SHUTDOWN_FLAG:
		#TODO FIX PRUNING
		print("Pruning smartGardenLog")
		prune.prune("smartGardenLog.txt")
		prune("soilLog.txt")
		#prune("sunlightLog.txt")
		if SHUTDOWN_FLAG:
			break
			
def api_thread():
	print("Starting API")
	logging.info("Starting API")
	app.run(host='192.168.0.18', port='5002')
	print("API thread closed.")
	


if __name__ == "__main__":
	#logging.basicConfig(filename="/home/pi/Desktop/smartGarden/smartGarden/logs/smartGardenLog.txt", level=logging.INFO)
	thread1 = threading.Thread(target=email_thread)
	thread2 = threading.Thread(target=sunlight_thread)
	thread3 = threading.Thread(target=pump_thread)
	thread4 = threading.Thread(target=camera_thread)
	thread5 = threading.Thread(target=artifical_light_thread)
	thread6 = threading.Thread(target=soil_moisture_thread)
	thread7 = threading.Thread(target=api_thread)
	thread8 = threading.Thread(target=prune_logs_thread)
	
	print("Starting threads at time: " + str(datetime.now()) + "...")
	logging.info("Starting threads at time: " + str(datetime.now()) + "...")
	thread1.daemon = True
	thread1.start()

	#thread2.start()

	thread3.daemon = True
	thread3.start()

	thread4.daemon = True
	thread4.start()

	thread5.daemon = True
	thread5.start()

	thread6.daemon = True
	thread6.start()

	thread7.start()

	thread8.daemon = True
	thread8.start()
	print("""  
 ____                       _      ____               _            
/ ___| _ __ ___   __ _ _ __| |_   / ___| __ _ _ __ __| | ___ _ __  
\___ \| '_ ` _ \ / _` | '__| __| | |  _ / _` | '__/ _` |/ _ \ '_ \ 
 ___) | | | | | | (_| | |  | |_  | |_| | (_| | | | (_| |  __/ | | |
|____/|_| |_| |_|\__,_|_|   \__|  \____|\__,_|_|  \__,_|\___|_| |_|
  
  Created by Alexander Taffe
  Version 0.1
  \n\n\nAll Threads Started!\n\n\n
  """)
	logging.info("""
 ____                       _      ____               _            
/ ___| _ __ ___   __ _ _ __| |_   / ___| __ _ _ __ __| | ___ _ __  
\___ \| '_ ` _ \ / _` | '__| __| | |  _ / _` | '__/ _` |/ _ \ '_ \ 
 ___) | | | | | | (_| | |  | |_  | |_| | (_| | | | (_| |  __/ | | |
|____/|_| |_| |_|\__,_|_|   \__|  \____|\__,_|_|  \__,_|\___|_| |_|
  
  Created by Alexander Taffe
  Version 0.1
  \n\n\nAll Threads Started!\n\n\n
  """)

	thread7.join()
	print("Thread 7 ended")
	logging.info("Shut Down Complete!")
	sys.exit()

	thread1.join()
	print("Thread 1 ended")
	#thread2.join()
	thread3.join()
	print("Thread 3 ended")
	thread4.join()
	print("Thread 4 ended")
	thread5.join()
	print("Thread 5 ended")
	thread6.join()
	print("Thread 6 ended")
	thread8.join()
	print("Thread 8 ended")
	
