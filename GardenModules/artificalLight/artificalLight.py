from GardenModules.GardenModule import GardenModule
from datetime import datetime
import RPi.GPIO as GPIO
import threading


class ArtificialLight(GardenModule):
    def __init__(self, log, queue):
        super().__init__(queue)
        self.logging = log
        self._light_start_time = 18
        self._light_end_time = 22
        self._lamp_pin = 16
        self._artificial_light_time = 300  # seconds

    def _run_artificial_light(self):
        try:
            current_time_stamp = str(datetime.now()).split()[1]
            current_hour = int(current_time_stamp.split(':')[0])
            self.logging.info("Current time: " + str(current_hour))
            if self._light_start_time <= current_hour < self._light_end_time:
                self._set_artificial_light("on")
                self.logging.info("Turning light on " + str(datetime.now()))
            elif current_hour < self._light_start_time or current_hour > self._light_end_time:
                self._set_artificial_light("off")
                self.logging.info("Turning light off " + str(datetime.now()))
        except Exception as e:
            self.logging.info("Could not setup light " + str(datetime.now()))
            self.logging.warn(e)

    def _set_artificial_light(self, on_off):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._lamp_pin, GPIO.OUT, initial=1)
            if on_off == "on":
                GPIO.output(self._lamp_pin, 0)
            else:
                GPIO.output(self._lamp_pin, 1)
        except Exception as e:
            self.logging.warn(e)

    def run(self):
        self._run_artificial_light()
        timer = threading.Event()
        while not timer.wait(self._artificial_light_time):
            self.logging.info("running light thread.")
            print("running light thread.")
            self._run_artificial_light()
            if self._sentinel.get(block=True):
                self._sentinel.put(True)
                self._set_artificial_light("off")
                self._sentinel.task_done()
                break
            self._sentinel.put(True)
            self._sentinel.task_done()
        GPIO.cleanup()
