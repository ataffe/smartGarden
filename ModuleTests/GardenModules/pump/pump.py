import RPi.GPIO as GPIO
import time
import threading
from GardenModules.GardenModule import GardenModule
from GardenModules.soilMoisture.soil import SoilMoisture
from datetime import datetime


class WaterPump(GardenModule):
    def __init__(self, log, queue, soil_moisture_sensor):
        super().__init__(queue)
        self.logging = log
        self._pwm = 70
        self._pin = 18
        self._pumpInterval = 60
        self.setName("pumpThread")
        self.soilMoisture = soil_moisture_sensor

    def _run(self, runtime=None, dutyCycle=50):
        if runtime == None:
            raise Exception("The value of run_time for the water pump was none.")
        try:
            self._setup(self._pin)
            self._togglePin(self._pin)
            p = GPIO.PWM(self._pin, self._pwm)
            p.start(dutyCycle)
            time.sleep(runtime)
            GPIO.output(self._pin, GPIO.LOW)
            p.stop()
            self.logging.info("Watered plants at: " + str(datetime.now()))
        except Exception as exception:
            self.logging.warn("There was an error watering the plants.")
            self.logging.warn(exception)
            self.logging.info(self._printWatered())

    def _run_sequence(self):
        self._run(10, 100)
        time.sleep(5)
        self._run(3, 70)
        time.sleep(5)
        self._run(2, 50)

    def run(self):
        try:
            print("Starting pump thread.")
            # self._run_sequence()
            timer = threading.Event()
            while not timer.wait(self._pumpInterval):
                if self.soilMoisture.getSoilPercentage() < 40:
                    # self._run_sequence()
                    print("Watering because soil moisture is at: {}\n".format(self.soilMoisture.getSoilPercentage())
                          + self._printWatered())
                else:
                    print("Skipping watering because soil moisture is at: {:.2f}%".format(
                        self.soilMoisture.getSoilPercentage()))
                # TODO Refactor sentinel to be part of the while loop so that when it is triggered the loop ends.
                if self._sentinel.get(block=True):
                    self.logging.info("Sentinel was triggered in pump thread.")
                    self._sentinel.put(True)
                    self._sentinel.task_done()
                    break
                self._sentinel.put(False)
                self._sentinel.task_done()
        except Exception as exception:
            self.logging.info("There was an exception in the pump thread: ")
            self.logging.info(exception)

    def setInterval(self, interval):
        self._pumpInterval = interval

    def getInterval(self):
        return self._pumpInterval

    def _togglePin(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        GPIO.output(pin, GPIO.LOW)

    def _setup(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)

    def _printWatered(self):
        return """ 
											,d	
									88						  
	8b	  db	  d8 ,adPPYYba, MM88MMM ,adPPYba, 8b,dPPYba,  
	`8b	d88b	d8' ""	 `Y8   88   a8P_____88 88P'   "Y8  
	`8b  d8'`8b  d8'  ,adPPPPP88   88   8PP""""""" 88		  
	`8bd8'  `8bd8'   88,	,88   88,  "8b,   ,aa 88		  
		YP	  YP	 `"8bbdP"Y8   "Y888 `"Ybbd8"' 88  
		"""
