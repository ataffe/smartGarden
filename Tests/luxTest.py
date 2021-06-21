import logging
import queue

from GardenModules.luxSensor.luxSensor import LuxSensor

logging.basicConfig(filename="testLog.log", level=logging.INFO)
sentinel = queue.Queue()
sentinel.put(False)

sensor = LuxSensor(logging, sentinel)
sensor.start()

while True:
    try:
        pass
    except KeyboardInterrupt:
        sentinel.put(True)
        print("Ending test")
        break

sensor.join()
