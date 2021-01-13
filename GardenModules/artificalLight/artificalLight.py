from GardenModules.GardenModule import GardenModule
from datetime import datetime
import RPi.GPIO as GPIO
import threading


class ArtificialLight(GardenModule):
    def __init__(self, log, queue):
        super().__init__(queue)
        self._log = log
        try:
            self._light_start_time = 9
            self._light_end_time = 17
            self._lamp_pin = 16
            self._artificial_light_time = 300  # 300 seconds
            self.setName("ArtificialLightThread")
            self._log.info("Grow light successfully started!")
        except Exception as exception:
            self._log.error("Grow light failed to start up.")
            self._log.error(exception)

    def _run_artificial_light(self):
        try:
            current_time_stamp = str(datetime.now()).split()[1]
            current_hour = int(current_time_stamp.split(':')[0])
            self._log.info("Current time: " + str(current_hour))
            if self._light_start_time <= current_hour <= self._light_end_time:
                self._log.info("Turning light on " + str(datetime.now()))
                self._set_artificial_light("on")
            elif current_hour < self._light_start_time or current_hour > self._light_end_time:
                self._log.info("Turning light off " + str(datetime.now()))
                self._set_artificial_light("off")
        except Exception as e:
            print("Exception in light thread.")
            self._log.info("Could not setup light " + str(datetime.now()))
            self._log.warn(e)

    def _set_artificial_light(self, on_off):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._lamp_pin, GPIO.OUT, initial=1)
            if on_off == "on":
                GPIO.output(self._lamp_pin, 0)
            else:
                GPIO.output(self._lamp_pin, 1)
        except Exception as e:
            self._log.warn(e)

    def run(self):
        self._run_artificial_light()
        timer = threading.Event()
        # TODO use Event.set to stop all thread gracefully.
        while not timer.wait(self._artificial_light_time):
            self._run_artificial_light()
            if self._sentinel.get(block=True):
                self._log.info("Sentinel was triggered in light.")
                self._sentinel.put(True)
                self._set_artificial_light("off")
                self._sentinel.task_done()
                break
            self._sentinel.put(False)
            self._sentinel.task_done()
        GPIO.cleanup()
