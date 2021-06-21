import logging

def prune(file):
	lines = []
	try:
		logFile = open("/home/pi/Desktop/smartGarden/smartGarden/logs/" + file, "r")
		for line in logFile:
			lines.append(line)
	except Exception as e:
		print("Error reading log file: " + file + " for pruning")
	finally:
		logFile.close()
		
	try:
		logFile = open("/home/pi/Desktop/smartGarden/smartGarden/logs/" + file, "w")
		if len(lines) > 5000:
			# Only keep the last 5000 lines
			for x in range(5000):
				index = len(lines) - 5001 + x
				logFile.write(lines[index])
	except Exception as e:
		print("Error writing log file: " + file)
	finally:
		logFile.close()
	logging.info("Pruned Log: " + file)
	print("Pruned log: " + file)