from flask import Flask, request, render_template
from flask_cors import CORS
from flask_debug import Debug
from GardenModules.GardenModule import GardenModule
import logging
import time

app = Flask(__name__, template_folder='/home/pi/Desktop/smartGarden/smartGarden/ControlPanel', static_folder="/home/pi/Desktop/smartGarden/smartGarden/ControlPanel")
CORS(app)
Debug(app)

pump = None
light = None
lux = None
moisture = None
temp = None

LIGHT_START_TIME = 18
LIGHT_END_TIME = 22

# Control Panel End Points
@app.route('/shutdown')
def shutdown():
	logging.info("Shutting down garden.")
	print("Shutting down garden.")
	_shutdown_server()
	return "Shutting down..."


@app.route('/heartBeat')
def heartBeat():
	return "ok"


@app.route('/water/heartBeat')
def waterHeartBeat():
	global pump
	return str(pump.is_running())


@app.route('/getWater')
def getWater():
	global pump
	try:
		logging.info("Returning pump time: " + str(pump.getInterval()))
		return str(pump.getInterval() / 3600)
	except Exception as e:
		logging.error(e)
		print(e)


@app.route('/setLight/<value>')
def setLight(value):
	# TODO add global light object and get times from it
	global LIGHT_START_TIME
	global LIGHT_END_TIME
	LIGHT_START_TIME = int(value.split(':')[0])
	LIGHT_END_TIME = int(value.split(':')[1])
	print("Setting new start time as: " + str(LIGHT_START_TIME) + " and end time as: " + str(LIGHT_END_TIME))
	return "ok"


@app.route('/setWater/<value>')
def setWater(value):
	global pump
	pump_time = int(value) * 3600
	print("Pump interval now set to: " + str(pump_time))
	pump.setInterval(pump_time)
	return "ok"


@app.route('/runPump/<time_seconds>')
def runPump(time_seconds):
	global pump
	pump.pump(int(time_seconds))
	return "Watering Complete"


# TODO get values from light object
@app.route('/getLightTimes')
def getLight():
	try:
		print("Returning light times start: " + str(LIGHT_START_TIME) + " light times end: " + str(LIGHT_END_TIME))
		return str(LIGHT_START_TIME) + ":" + str(LIGHT_END_TIME)
	except Exception as e:
		print(e)

@app.route('/garden')
def garden_route():
	with open("/home/pi/Desktop/smartGarden/smartGarden/logs/smartGardenLog.txt") as file:
		return file.read()



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


def _shutdown_server():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()


class GardenServer(GardenModule):
	def __init__(self, queue, water_pump, lux_sensor, soil_moisture_sensor, temp_sensor):
		super().__init__(queue)
		global pump
		pump = water_pump
		global lux
		lux = lux_sensor
		global moisture
		moisture = soil_moisture_sensor
		global temp
		temp = temp_sensor

	def run(self):
		try:
			print("Starting API")
			logging.info("Starting Garden Server.")
			app.run(host='0.0.0.0', port='5002')
			print("API thread closed.")
		except Exception as exception:
			logging.error("Garden server failed to start up.")
			logging.error(exception)
			self._started = False

	def shutDownGarden(self, sig, frame):
		logging.warning("Shutdown triggered.")
		self._sentinel.get(block=True)
		self._sentinel.put(True)
		self._sentinel.task_done()
		time.sleep(3)
		shutdown()
