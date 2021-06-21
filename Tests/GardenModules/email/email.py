from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
from datetime import datetime
from datetime import timedelta
import smtplib, ssl
import logging

def send_email():
	port = 465 # For SSL
	password = "al.EX.91.27"
	sender_email = "raspberry.pi.taffe@gmail.com"
	receiver_email = "taffeAlexander@gmail.com"
	message = MIMEMultipart("alternative")
	message["Subject"] = "Garden update: " + formatdate(localtime=True)
	message["From"] = sender_email
	message["To"] = receiver_email
	message["Date"] = formatdate(localtime=True)
	soilMoisture = "No Data"
	soilTimeStamp = "No Data"
	soilIterator = 0
	soilMoistureArray = []
	soilTimeStampArray = []
	currentYMD = str(datetime.now()).split()[0]

	# Create the body of the message (a plain-text and an HTML version).
	text = "Garden update plan text"

	try:
		html = """\
			<!DOCTYPE html>
			<html>
				<head>
				</head>
				<body>
					<h1>Garden Update</h1>
					<table style="width:100%">
						<tr>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> Sunlight </th>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> TimeStamp </th>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> Soil Moisture </th>
							<th style="font-size: medium;padding: 8px;background-color: #4CAF50;color: white;"> TimeStamp </th>
						</tr>
						"""
		soilLogArray = []
		with open("/home/pi/Desktop/smartGarden/smartGarden/logs/soilLog.txt", "r") as fp2:
			for count, line in enumerate(fp2):
				soilLogArray.append(line)
				
		for line in soilLogArray:
			try:
				splitLine = line.split()
				if (currentYMD == splitLine[4]) and (len(splitLine) > 5):
					soilMoistureArray.append(splitLine[3])
					soilTimeStampArray.append(splitLine[4] + " " + splitLine[5])
			except Exception as e:
				logging.warn("Unable to parse soil moisture or time stamp for email")
				logging.warn(e)
				print("Error parsing soil log: " + str(e))

		with open("/home/pi/Desktop/smartGarden/smartGarden/logs/sunlightLog.txt", "r") as fp:
			for cnt, line in enumerate(fp):
				lineArray = line.split()
				highlightedRow = "<td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>"
				regularRow = "<td style='border: 1px solid;padding: 8px; text-align: center;'>"
				greyRow = "<td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center'>"			

				if currentYMD == lineArray[3] or currentYMD == lineArray[4]:
					if soilIterator < len(soilMoistureArray):
						soilMoisture = soilMoistureArray[soilIterator]
						soilTimeStamp = soilTimeStampArray[soilIterator]
						soilIterator = soilIterator + 1
						print("Setting moisture: " + soilMoisture)
					else:
						soilMoisture = "NO DATA"
						soilTimeStamp = "NO DATA"
					if cnt % 2 == 0:
							if "YES" in lineArray[0]:
									row = "<tr style='width:100%'>" + highlightedRow  + lineArray[0] + " " + lineArray[1] + "</td>"
							else:
									row = "<tr style='width:100%'>" + regularRow + lineArray[0] + " " + lineArray[1] + "</td>"

							row = row + regularRow + lineArray[3] + " " +  lineArray[4]+ "</td>"
							row = row + regularRow + soilMoisture +"%</td>"
							row = row + regularRow + soilTimeStamp + "</td></tr>"
					else:
							if "YES" in lineArray[0]:
									row = "<tr style='width:100%'>" + highlightedRow + lineArray[0] + " " + lineArray[1] + "</td>"
							else:
									row = "<tr style='width:100%'>" + greyRow + lineArray[0] + " " + lineArray[1] + "</td>"
							row = row + greyRow + lineArray[3] + " " +	lineArray[4]+ "</td>"
							row = row + greyRow + soilMoisture + "%</td>"
							row = row + greyRow + soilTimeStamp + "</td></tr>"
					html = html + row
				elif currentYMD == lineArray[4]:
					if cnt % 2 == 0:
							if "YES" in lineArray[0]:
									row = "<tr style='width:100%'>" + highlightedRow + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
							else:
									row = "<tr style='width:100%'>" + regularRow + lineArray[0] + " " + lineArray[1] + "</td>"
							row = row + regularRow + lineArray[4] + " " +  lineArray[5]+ "</td>"
							row = row + regularRow + soilMoisture + "%</td>"
							row = row + regularRow + soilTimeStamp + "</td></tr>"
					else:
							if "YES" in lineArray[0]:
									row = "<tr style='width:100%'>" + highlightedRow + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
							else:
									row = "<tr style='width:100%'>" + greyRow + lineArray[0] + " " + lineArray[1] + "</td>"
							row = row + greyRow + lineArray[4] + " " +	lineArray[5]+ "</td>"
							row = row + greyRow + soilMoisture + "%</td>"
							row = row + greyRow + soilTimeStamp + "</td></tr>"
					html = html + row
				html = html + """\
						</table>
					</body>
				</html>
				"""
	except Exception as e:
		logging.warn("There was an error reading html file. Defaulting to basic html page")
		html = """\
		<html>
			<head></head>
			<body>
				<h1>Garden Update</h1>
			</body>
		</html>
		"""
		logging.warn(e)
		print("Error sending email: " + str(e))

	try:
		#Open the file to be sent
		attachment = open("/home/pi/Desktop/smartGarden/smartGarden/logs/smartGardenLog.txt", "rb")
		p = MIMEBase('application', 'octet-stream')
		p.set_payload((attachment).read())
		encoders.encode_base64(p)

		p.add_header('Content-Disposition', "attachment; filename=%s" % "GardenLog.txt")
		message.attach(p)
	except Exception as e:
		logging.warn("There was an error opening attachment.")
		logging.warn(e)
	finally:
		attachment.close()

	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	message.attach(part1)
	message.attach(part2)

	# Create a secure SSL context
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", port) as server:
		server.login("raspberry.pi.taffe@gmail.com", password)
		server.sendmail(sender_email, receiver_email, message.as_string())
		logging.info("Email Sent "+ str(datetime.now()))