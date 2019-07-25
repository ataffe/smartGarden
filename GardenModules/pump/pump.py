import RPi.GPIO as GPIO
import logging
import time
from datetime import datetime

def run_pump(run_time=None,pwm=50):

	if run_time == None:
		raise Exception("The value of run_time for the water pump was  None")
	try:
		dutycycle = 60
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(18, GPIO.OUT)
		GPIO.output(18, GPIO.HIGH)
		GPIO.output(18, GPIO.LOW)
		p = GPIO.PWM(18,pwm)
		p.start(dutycycle)
		time.sleep(run_time)
		GPIO.output(18, GPIO.LOW)
		p.stop()
		logging.info("Watered plants at: " + str(datetime.now()))
		logging.info(""" 
		
		                                ,d                          
                                88                          
8b      db      d8 ,adPPYYba, MM88MMM ,adPPYba, 8b,dPPYba,  
`8b    d88b    d8' ""     `Y8   88   a8P_____88 88P'   "Y8  
 `8b  d8'`8b  d8'  ,adPPPPP88   88   8PP""""""" 88          
  `8bd8'  `8bd8'   88,    ,88   88,  "8b,   ,aa 88          
    YP      YP     `"8bbdP"Y8   "Y888 `"Ybbd8"' 88  
	
	""")
	except Exception as e:
		logging.warn("There was an error watering the plants.")
		logging.warn(e)