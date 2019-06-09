def build_table(ymd):
	soilLogArray = []
	with open("/home/pi/Desktop/smartGarden/smartGarden/soilLog.txt", "r") as fp2:
		for count, line in enumerate(fp2):
			soilLogArray.append(line)

	with open("/home/pi/Desktop/smartGarden/smartGarden/sunlightLog.txt", "r") as fp:
		for cnt, line in enumerate(fp):
			lineArray = line.split()
			currentYMD = str(datetime.now()).split()[0]
			soilMoisture = "No Data"
			soilTimeStamp = "No Data"
			if cnt < len(soilLogArray):
				try:
					splitLine = soilLogArray[cnt].split()
					soilMoisture = splitLine[3]
					soilTimeStamp = splitLine[4] + " " + splitLine[5]
					print("soilMoisture: " + soilMoisture)
					print("soil time stamp: " + soilTimeStamp)
				except Exception as e:
					logging.warn("Unable to parse soil moisture or time stamp for email.")
					logging.warn(e)

			if currentYMD == lineArray[3]:
				if cnt % 2 == 0:
					if "YES" in lineArray[0]:
						row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
					else:
						row = "<tr><td style='border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"

					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center'>" + lineArray[3] + " " +  lineArray[4]+ "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilMoisture + "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilTimeStamp + "</td></tr>"
				else:
					if "YES" in lineArray[0]:
						row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
					else:
						row = "<tr><td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
					row = row + "<td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center'>" + lineArray[3] + " " +  lineArray[4]+ "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilMoisture + "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilTimeStamp + "</td></tr>"
				html = html + row
			elif currentYMD == lineArray[4]:
				if cnt % 2 == 0:
					if "YES" in lineArray[0]:
						row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
					else:
						row = "<tr><td style='border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center'>" + lineArray[4] + " " +  lineArray[5]+ "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilMoisture + "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilTimeStamp + "</td></tr>"
				else:
					if "YES" in lineArray[0]:
						row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
					else:
						row = "<tr><td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
					row = row + "<td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center'>" + lineArray[4] + " " +  lineArray[5]+ "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilMoisture + "</td>"
					row = row + "<td style='border: 1px solid;padding: 8px; text-align: center; '>" + soilTimeStamp + "</td></tr>"
				html = html + row
			html = html + """\
					</table>
				</body>
			</html>
			"""
			
def build_sunlight_row(line, lineCount, currentYMD):

lineArray = line.split()
sunlightText = ""
date = ""

if currentYMD == lineArray[3]:
	sunlightText = lineArray[0] + " " + lineArray[1]
elif currentYMD == lineArray[4]:
	sunlightText = lineArray[0] + " " + lineArray[1] + " " + lineArray[2]

hightlighted_row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>"
regular_row = "<tr><td style='border: 1px solid;padding: 8px; text-align: center; '>"
grey_row = "<tr><td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center; '>"
html = ""


if currentYMD == lineArray[3]:
	if cnt % 2 == 0:
		if "YES" in lineArray[0]:
			row = hightlighted_row + sunlightText + "</td>"
		else:
			row = regular_row + sunlightText + "</td>"
	else:
		if "YES" in lineArray[0]:
			row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + sunlightText + "</td>"
		else:
			row = "<tr><td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center; '>" + sunlightText + "</td>"
	html = html + row
elif currentYMD == lineArray[4]:
	if cnt % 2 == 0:
		if "YES" in lineArray[0]:
			row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
		else:
			row = "<tr><td style='border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"
	else:
		if "YES" in lineArray[0]:
			row = "<tr><td style='color: #FFD700;background-color: #00aced;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + " " + lineArray[2] + "</td>"
		else:
			row = "<tr><td style='background-color: #f2f2f2;border: 1px solid;padding: 8px; text-align: center; '>" + lineArray[0] + " " + lineArray[1] + "</td>"