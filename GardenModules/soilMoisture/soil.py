import csv
import os

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import threading
from adafruit_ads1x15.analog_in import AnalogIn
from GardenModules.GardenModule import GardenModule
from datetime import datetime
from datetime import date
from queue import Queue


class SoilMoisture(GardenModule):
    def __init__(self, log, queue):
        super().__init__(queue)
        self.log = log
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._ads = ADS.ADS1115(self._i2c, address=0x49)
        self._ads.gain = 1
        self.channel = AnalogIn(self._ads, ADS.P0)
        self.soilInterval = 120  # 1800
        self.log.info("Channel: " + str(self.channel))
        self.setName("soilThread")
        self._data_file = "/home/pi/Desktop/smartGarden/smartGarden/Data/soilMoistureData.csv"

        # Set Gain to 16 bits
        # Gain = 1 # Wet: 13884 Dry: 21680
        # Gain = 2/3 # Wet: 11031 Dry: 14989
        self.queue = Queue()
        self.sum = 0
        self.window_size = 10
        self.percentage = 0
        self.average_soil_value = 0
        for x in range(0, 10):
            self._checkSoil()

    def _checkSoil(self):
        try:
            # I am using a moving average to remove sensor noise.
            value = self.channel.value
            if self.queue.qsize() >= self.window_size:
                self.sum += value
                self.sum -= self.queue.get()
                self.average_soil_value = self.sum / self.window_size
                self.percentage = ((self.sum / self.window_size) / 21680) * 100
                self.log.info("Soil Moisture Level: {} | Averaged Value: {:.2f}% | raw value {}".format(
                    self.sum / self.window_size, self.getSoilPercentage(), value))
                print("Soil Moisture Level: {} | Averaged Value: {:.2f}% | raw value {}".format(
                    self.sum / self.window_size,
                    self.getSoilPercentage(), value))

                # with open(self._data_file, mode='a+') as file:
                #     self.log.info("Writing to data file.")
                #     writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                #     writer.writerow([self.getSoilPercentage(), str(self.sum / self.window_size), self.channel.value, datetime.now()])

            else:
                self.sum += value
            self.queue.put(value)

        except Exception as exception:
            self.log.exception("Error calculating soil moisture")

        try:
            with open("/home/pi/Desktop/smartGarden/smartGarden/logs/soilLog.txt", "a+") as logFile:
                logFile.write("Soil Moisture Level: " + str(self.getSoilPercentage()) + "% " + str(
                    datetime.now()) + " Raw Value: " + str(self.channel.value) + "\n")
        except Exception as exception:
            self.log.exception("Error writing soil moisture level")

    def run(self):
        self._checkSoil()
        timer = threading.Event()

        while not timer.wait(self.soilInterval):
            self._checkSoil()
            # TODO create a function for the sentinel
            if self._sentinel.get(block=True):
                print("Sentinel was triggered in soil thread.")
                self._sentinel.put(True)
                self._sentinel.task_done()
                break
            self._sentinel.put(False)
            self._sentinel.task_done()

    def getSoilPercentage(self):
        return 100 - self.percentage

    def getSoilValue(self):
        return self.sum / self.window_size
