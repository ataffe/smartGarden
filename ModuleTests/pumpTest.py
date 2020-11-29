import queue
import logging

from GardenModules.pump.pump import WaterPump
from GardenModules.soilMoisture.soil import SoilMoisture

logging.basicConfig(filename="testLog.log", level=logging.INFO)
sentinel = queue.Queue()
sentinel.put(False)

soilMoistureSensor = SoilMoisture(logging, sentinel)
pump = WaterPump(logging, sentinel, soilMoistureSensor)

pump.start()

while True:
    try:
        pass
    except KeyboardInterrupt:
        print("Ending test")
