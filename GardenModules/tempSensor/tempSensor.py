import glob
import time
from GardenModules.GardenModule import GardenModule
import threading


class TempSensor(GardenModule):
    def __init__(self, log, queue):
        super().__init__(queue)
        self._log = log
        try:
            self._base_dir = '/sys/bus/w1/devices/'
            self._device_folder = glob.glob(self._base_dir + '28*')[0]
            self._device_file = self._device_folder + '/w1_slave'
            self._temp_interval = 120
            self._log.info("Temperature sensor start up successful")
        except Exception as exception:
            self._log.error("Temperature sensor start up failed.")
            self._log.error(exception)
            self._started = False

    def _read_temp_raw(self):
        f = open(self._device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temperature(self):
        lines = self._read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

    def run(self):
        if self._started:
            print("Starting temperature sensor thread")
            timer = threading.Event()
            while not timer.wait(self._temp_interval):
                self._log.info(self.get_string())
                print(self.get_string())
                if self._sentinel.get(block=True):
                    print("Sentinel was triggered in soil thread.")
                    self._sentinel.put(True)
                    self._sentinel.task_done()
                    break
                self._sentinel.put(False)
                self._sentinel.task_done()

    def get_string(self):
        temp_c, temp_f = self.read_temperature()
        return 'Temperature: ' + str(temp_c) + 'C | ' + str(temp_f) + 'F'
