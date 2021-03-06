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

app = Flask(__name__, template_folder='/home/pi/Desktop/smartGarden/smartGarden/ControlPanel',
            static_folder="/home/pi/Desktop/smartGarden/smartGarden/ControlPanel")
CORS(app)
Debug(app)


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
    logging.info("Zipping File... " + str(datetime.now()))
    baseFolder = ymd
    baseFolder = "/home/pi/Desktop/smartGarden/smartGarden/images/" + baseFolder
    ymd = baseFolder + ".zip"
    currentDirectory = os.path.dirname(os.path.realpath(__file__))
    os.chdir("/home/pi/Desktop/smartGarden/smartGarden/images")
    zf = zipfile.ZipFile(ymd, mode='w', compression=zipfile.ZIP_LZMA)
    try:
        zipdir(baseFolder, zf)
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
        # os.system("rm -r " + baseFolder)
        os.chdir(currentDirectory)
        time2 = datetime.now()
        diff = time2 - time1
        logging.info("It took (mins, seconds): " + str(divmod(diff.total_seconds(), 60)) + " to transfer " + str(ymd))
    except Exception as e:
        logging.warn("There was an error deleting the folders and moving back a directory")
        logging.warn(e)


def take_pics(ymd, number=1):
    for x in range(number):
        logging.info("Taking image " + str(x + 1) + " out of " + str(number))
        filename = str(datetime.now()).replace(" ", "-")
        filename = filename.replace(":", "-")
        filename = filename.replace(".", "-")
        filename = filename + ".jpg"
        # Take image
        # old was 800x600
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
        # print("Sending picture to: " + "/home/pi/Desktop/smartGarden/smartGarden/images/" + ymd + "/" + str(filename))
    # myCmd = 'fswebcam -q -i 0 -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/images/' + ymd + "/" + str(filename)
    # os.system(myCmd)


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


def camera_thread():
    # TODO ADD ANOTHER THREAD FOR SENDING IMAGES TO CACTUAR PC
    ymd = create_folder()
    timer = threading.Event()
    # run_camera(send_folder=False)
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
    logFile = "/home/pi/Desktop/smartGarden/smartGarden/logs/smartGardenLog.log"
    if not os.path.exists(logFile):
        with open(logFile, 'w+'):
            pass

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=logFile, level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S')
    sentinel = queue.Queue()
    sentinel.put(False)

    soilMoistureSensor = SoilMoisture(logging, sentinel)
    pump = WaterPump(logging, sentinel, soilMoistureSensor)
    server = GardenServer(pump, sentinel)
    luxSensor = None
    try:
        luxSensor = LuxSensor(logging, sentinel)
    except Exception as e:
        logging.error("Failed to start lux sensor")
        logging.error(e)
    tempSensor = TempSensor(logging, sentinel)
    artificialLight = ArtificialLight(logging, sentinel)
    signal.signal(signal.SIGINT, server.shutDownGarden)

    # thread4 = threading.Thread(target=camera_thread)
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
