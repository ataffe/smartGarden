from flask import Flask, request, render_template
from flask_cors import CORS
from flask_debug import Debug
from GardenModules.GardenModule import GardenModule
import logging
import time

app = Flask(__name__, template_folder='./ControlPanel', static_folder="./ControlPanel")
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
def heart_beat():
	return "ok"


@app.route('/water/heartBeat')
def water_heart_beat():
	global pump
	return str(pump.is_running())


@app.route('/lux/heartBeat')
def lux_heart_beat():
	global lux
	return str(lux.is_running())


@app.route('/moisture/heartBeat')
def moisture_heart_beat():
	global moisture
	return str(moisture.is_running())


@app.route('/temp/heartBeat')
def temp_heart_beat():
	global temp
	return str(temp.is_running())


@app.route('/getWater')
def get_water():
	global pump
	try:
		logging.info("Returning pump time: " + str(pump.getInterval()))
		return str(pump.getInterval() / 3600)
	except Exception as e:
		logging.error(e)
		print(e)


@app.route('/setLight/<value>')
def set_light(value):
	# TODO add global light object and get times from it
	global LIGHT_START_TIME
	global LIGHT_END_TIME
	LIGHT_START_TIME = int(value.split(':')[0])
	LIGHT_END_TIME = int(value.split(':')[1])
	print("Setting new start time as: " + str(LIGHT_START_TIME) + " and end time as: " + str(LIGHT_END_TIME))
	return "ok"


@app.route('/setWater/<value>')
def set_water(value):
	global pump
	pump_time = int(value) * 3600
	print("Pump interval now set to: " + str(pump_time))
	pump.setInterval(pump_time)
	return "ok"


@app.route('/runPump/<time_seconds>')
def run_pump(time_seconds):
	global pump
	pump.pump(int(time_seconds))
	return "Watering Complete"


# TODO get values from light object
@app.route('/getLightTimes')
def get_light():
	try:
		print("Returning light times start: " + str(LIGHT_START_TIME) + " light times end: " + str(LIGHT_END_TIME))
		return str(LIGHT_START_TIME) + ":" + str(LIGHT_END_TIME)
	except Exception as e:
		print(e)


@app.route('/soil')
def soil_route():
	try:
		with open("./soilLog.txt") as file:
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
	with open("./logs/smartGardenLog.txt") as file:
		return file.read()


@app.route('/')
@app.route('/controlPanel')
def control_panel():
	return render_template("index.html")


@app.route('/water')
def control_panel_water():
	with open('./ControlPanel/water.html') as file:
		return file.read()


@app.route('/light')
def control_panel_light():
	with open('./ControlPanel/light.html') as file:
		return file.read()


@app.route('/soilMoisture')
def control_panel_soil_moisture():
	with open('./ControlPanel/soilMoisture.html') as file:
		return file.read()


@app.route('/sun_css')
def sun_css():
	with open('./ControlPanel/sun.css') as file:
		return file.read()


@app.route('/status_css')
def status_css():
	with open('./ControlPanel/status.css') as file:
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
