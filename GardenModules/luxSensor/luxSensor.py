import adafruit_tsl2561
import busio
import board
import threading
from GardenModules.GardenModule import GardenModule
from datetime import datetime
import csv


class LuxSensor(GardenModule):
    def __init__(self, log, queue):
        super().__init__(queue)
        self._logging = log
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._sensor = adafruit_tsl2561.TSL2561(self._i2c)
        self._sensor.gain = 0
        self._grow_light_lux = 535
        self._lux_interval = 300
        self._data_file = "/home/pi/Desktop/smartGarden/smartGarden/Data/luxData.csv"

    def getLux(self):
        return self._sensor.lux

    def isSunlight(self):
        return self._sensor.lux > self._grow_light_lux

    def _saveReading(self):
        if not os.path.exists(self._data_file):
            with open(self._data_file, 'w+'):
                pass

        with open(self._data_file, mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([self._sensor.lux, datetime.now()])

    def run(self):
        timer = threading.Event()
        while not timer.wait(self._lux_interval):
            self._logging.info(self)
            print(self)
            self._saveReading()
            if self._sentinel.get(block=True):
                print("Sentinel was triggered in soil thread.")
                self._sentinel.put(True)
                self._sentinel.task_done()
                break
            self._sentinel.put(False)
            self._sentinel.task_done()

    def __str__(self):
        return "Current lux reading: {}".format(self.getLux())

