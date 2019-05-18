import zipfile
import os
from datetime import datetime, timedelta

def zipdir(path, ziph):
	for root, dirs, files in os.walk(path, topdown=True):
		for file in files:
			ziph.write(os.path.join(root, file))

def send_folder(ymd):
	time1 = datetime.now()
	print("Zipping File...")
	baseFolder = ymd
	baseFolder = "/home/pi/Desktop/smartGarden/smartGarden/images/" + baseFolder

	ymd = baseFolder + ".zip"
	currentDirectory = os.path.dirname(os.path.realpath(__file__))
	os.chdir("/home/pi/Desktop/smartGarden/smartGarden/images")
	if os.path.isfile(ymd):
		print(ymd + " already exists")
	else:
		zf = zipfile.ZipFile(ymd, mode = 'w', compression=zipfile.ZIP_LZMA)
		try:
			zipdir(baseFolder,zf)
		finally:
			zf.close()

	print("Sending images...")
	scp_command = "SSHPASS='al.EX.91.27' sshpass -e scp " + ymd + " alext@192.168.0.20:D:\\\\smartGarden\\\\Images"
	os.system(scp_command)
	os.system("rm -f " + ymd)
	#os.system("rm -rf " + baseFolder)
	os.chdir(currentDirectory)
	time2 = datetime.now()
	diff = time2 - time1
	print("It took (mins, seconds): " + str(divmod(diff.total_seconds(),60)) + " to transfer " + str(ymd))

yesterday = datetime.now() - timedelta(days=2)
filename = str(yesterday).replace(" ", "-")
dateArray = filename.split('-')
ymd = dateArray[0] + "-" + dateArray[1] + "-" + dateArray[2]
send_folder(ymd)
