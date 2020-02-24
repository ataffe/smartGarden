import RPi.GPIO as GPIO
import logging
import time
from datetime import datetime

class WaterPump:
    _dutyCycle = 60
    _pin = 18
    
    def run(self,runtime=None, pwm=50):
        if runtime == None:
            raise Exception("The value of run_time for the water pump was  None")
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(_pin, GPIO.OUT)
            GPIO.output(_pin, GPIO.HIGH)
            GPIO.output(_pin, GPIO.LOW)
            p = GPIO.PWM(_pin,pwm)
            p.start(_dutyCycle)
            time.sleep(runtime)
            GPIO.output(_pin, GPIO.LOW)
            p.stop()
            logging.info("Watered plants at: " + str(datetime.now()))
        except Exception as exception:
            logging.warn("There was an error watering the plants.")
            logging.warn(exception)
            _printWatered(self)
	
    def _printWatered(self):
        logging.info(""" 
		
                                            ,d                          
                                    88                          
    8b      db      d8 ,adPPYYba, MM88MMM ,adPPYba, 8b,dPPYba,  
    `8b    d88b    d8' ""     `Y8   88   a8P_____88 88P'   "Y8  
    `8b  d8'`8b  d8'  ,adPPPPP88   88   8PP""""""" 88          
    `8bd8'  `8bd8'   88,    ,88   88,  "8b,   ,aa 88          
        YP      YP     `"8bbdP"Y8   "Y888 `"Ybbd8"' 88  
        
        """)
