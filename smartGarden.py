import threading
from datetime import datetime
from datetime import timedelta
import os
import zipfile
import logging
from GardenModules.luxSensor.luxSensor import LuxSensor
from GardenModules.pump.pump import WaterPump
from GardenModules.soilMoisture.soil import SoilMoisture
from GardenModules.gardenServer.gardenServer import GardenServer
from GardenModules.artificalLight.artificalLight import ArtificialLight
from GardenModules.tempSensor.tempSensor import TempSensor
import GardenModules.prune.prune as prune
import cv2
from flask import Flask, request, render_template
from flask_cors import CORS
from flask_debug import Debug
import sys
import queue
import signal

# Disable logging for api
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Constants
WAIT_TIME_SECONDS = 600
EMAIL_TIME_SECONDS = 36000
CAMERA_TIME_SECONDS = 300
WAIT_TIME_PRUNE = 86400
image_count = 0
SHUTDOWN_FLAG = False

app = Flask(__name__, template_folder='./ControlPanel',
            static_folder="./ControlPanel")
CORS(app)
Debug(app)


def prune_logs_thread():
    # prune.prune("smartGardenLog.txt")
    timer = threading.Event()
    while not timer.wait(WAIT_TIME_PRUNE) and not SHUTDOWN_FLAG:
        # TODO FIX PRUNING
        print("Pruning smartGardenLog")
        prune.prune("smartGardenLog.txt")
        prune("soilLog.txt")
        # prune("sunlightLog.txt")
        if SHUTDOWN_FLAG:
            break


if __name__ == "__main__":
    logFile = "./logs/smartGardenLog.log"
    if not os.path.exists(logFile):
        with open(logFile, 'w+'):
            pass

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=logFile, level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S')
    sentinel = queue.Queue()
    sentinel.put(False)

    soilMoistureSensor = SoilMoisture(logging, sentinel)
    pump = WaterPump(logging, sentinel, soilMoistureSensor)

    luxSensor = None
    luxSensor = LuxSensor(logging, sentinel)
    tempSensor = TempSensor(logging, sentinel)
    artificialLight = ArtificialLight(logging, sentinel)
    server = GardenServer(sentinel, pump, luxSensor, soilMoistureSensor, tempSensor)
    signal.signal(signal.SIGINT, server.shutDownGarden)

    thread8 = threading.Thread(target=prune_logs_thread)

    print("Starting threads at time: " + str(datetime.now()) + "...")
    logging.info("Starting threads at time: " + str(datetime.now()) + "...")

    pump.start()
    if luxSensor is not None:
        luxSensor.start()
    tempSensor.start()
    artificialLight.start()
    soilMoistureSensor.start()
    server.start()

    thread8.daemon = True
    thread8.start()
    print("""  
 ____                       _      ____               _            
/ ___| _ __ ___   __ _ _ __| |_   / ___| __ _ _ __ __| | ___ _ __  
\___ \| '_ ` _ \ / _` | '__| __| | |  _ / _` | '__/ _` |/ _ \ '_ \ 
 ___) | | | | | | (_| | |  | |_  | |_| | (_| | | | (_| |  __/ | | |
|____/|_| |_| |_|\__,_|_|   \__|  \____|\__,_|_|  \__,_|\___|_| |_|
  
  Created by Alexander Taffe
  Version 1.0
  \n\n\nAll Threads Started!\n\n\n
  """)
    logging.info("""
 ____                       _      ____               _            
/ ___| _ __ ___   __ _ _ __| |_   / ___| __ _ _ __ __| | ___ _ __  
\___ \| '_ ` _ \ / _` | '__| __| | |  _ / _` | '__/ _` |/ _ \ '_ \ 
 ___) | | | | | | (_| | |  | |_  | |_| | (_| | | | (_| |  __/ | | |
|____/|_| |_| |_|\__,_|_|   \__|  \____|\__,_|_|  \__,_|\___|_| |_|
  
  Created by Alexander Taffe
  Version 2.0
  \n\n\nAll Threads Started!\n\n\n
  """)

    server.join()
    print("server shutdown")
    logging.info("Shut Down Complete!")
    sys.exit()

    pump.join()
    print("Pump thread ended")

    # thread4.join()
    # print("Thread 4 ended")
    artificialLight.join()
    print("Artificial light ended")
    soilMoistureSensor.join()
    print("Soil moisture thread ended")
    luxSensor.join()
    print("Lux sensor thread ended")
    tempSensor.join()
    print("Temperature sensor thread ended")
    thread8.join()
    print("Thread 8 ended")
