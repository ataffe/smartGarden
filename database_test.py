#!/usr/bin/env python

import sqlite3
from datetime import datetime  
from datetime import timedelta

table_command = """CREATE TABLE IF NOT EXISTS sunlight (
			sunlight text NOT NULL,
			record_timestamp text PRIMARY KEY,
			cleanup_timestamp text); """
def create_table():
	try:
		conn = sqlite3.connect('gardenDatabase.db')
		cursor = conn.cursor()
		cursor.execute(table_command)
		print("Created sunlight table")
	except Exception as e:
		print(e)
	finally:
		conn.close()

def insertSunlightRecord(message,time1, time2):
	insert_command = "INSERT INTO sunlight VALUES (\'" + message + "\',\'"+ time1 + "\',\'" + time2 + "\');"
	try:
		conn = sqlite3.connect('gardenDatabase.db')
		cursor = conn.cursor()
		cursor.execute(insert_command)
		conn.commit()
		print("Inserted sunlight record")
		return cursor.lastrowid
	except Exception as e:
		print(e)
	finally:
		conn.close()

create_table()
time0 = datetime.now()
#print(time0)
time2 = time0 + timedelta(days=60)
#print(time2)

#sunlight_record = ("0", "yes sunlight test",str(time0),str(time2))
#print(str(sunlight_record))
#create_table()
insert_index = insertSunlightRecord("yes sunlight test",str(time0),str(time2))
print("Insert Index: " + str(insert_index))
