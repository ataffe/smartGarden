import logging
import sqlite3
from datetime import datetime
from datetime import timedelta
import RPi.GPIO as GPIO

def insertSunlightRecord(message,time1, time2):
	insert_command = "INSERT INTO sunlight VALUES (\'" + message + "\',\'"+ time1 + "\',\'" + time2 + "\');"
	try:
		conn = sqlite3.connect('/home/pi/Desktop/smartGarden/smartGarden/gardenDatabase.db')
		cursor = conn.cursor()
		cursor.execute(insert_command)
		conn.commit()
		logging.info("Inserted sunlight record")
		return cursor.lastrowid
	except Exception as e:
		logging.warn(e)
	finally:
		conn.close()

def prune():
	time = datetime.now()
	pruneDate = str(time - timedelta(days=30)).split()
	
	delete_command = "DELETE FROM sunlight WHERE record_timestamp LIKE '" + pruneDate[0] + "%';"
	#select_command = "SELECT * FROM sunlight WHERE record_timestamp LIKE '" + pruneDate[0] + "%';"
	#print("Prune Date: " + str(pruneDate))
	try:
		conn = sqlite3.connect('/home/pi/Desktop/smartGarden/smartGarden/gardenDatabase.db')
		cursor = conn.cursor()
		cursor.execute(delete_command)
		conn.commit()
	except Exception as e:
		print("Error: " + str(e))
	finally:
		conn.close()
	

def check_sunlight():
	artificialLightHours = False
	f = None
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		f = open("/home/pi/Desktop/smartGarden/smartGarden/logs/sunlightLog.txt", "a+")
		time = datetime.now()
		dateTimeString = str(time)
		cleanDateString = str(time + timedelta(days=30))
		currentTimeStamp = str(datetime.now()).split()[1]
		currentHour = currentTimeStamp.split(':')[0]
		hourAsInt = int(currentHour)

		if hourAsInt >= 18:
			f.write("YES Artificial Sunlight at: " + dateTimeString + "\n")
			insertSunlightRecord("YES Artificial Sunlight",dateTimeString,cleanDateString)
			artificialLightHours = True
			logging.info("Checked artificial sunlight")
		if hourAsInt >=6 and hourAsInt <= 12:
			f.write("YES Artificial Sunlight at: " + dateTimeString + "\n")
			insertSunlightRecord("YES Artificial Sunlight",dateTimeString,cleanDateString)
			artificialLightHours = True
			logging.info("Checked artificial sunlight")

		if not artificialLightHours:
			if not GPIO.input(4):
				f.write("YES Natural Sunlight at: " + dateTimeString + "\n")
				insertSunlightRecord("Yes Sunlight",dateTimeString,cleanDateString)
				logging.info("Checked natural sunlight")
			else:
				f.write("NO Sunlight at: " + dateTimeString	 + "\n")
				insertSunlightRecord("No Sunlight", dateTimeString, cleanDateString)
				logging.info("Checked natural sunlight")
	except Exception as e:
		logging.warn("There was an error writing to file.")
		logging.warn(e)
	finally:
		f.close()
		
