import zipfile
import os
from datetime import datetime

def zipdir(path, ziph):
	for root, dirs, files in os.walk(path):
		for file in files:
			ziph.write(os.path.join(root, file))

def send_folder(ymd):
	print("Zipping File...")
	baseFolder = ymd
	ymd = baseFolder + ".zip"
	os.chdir("images")
	zf = zipfile.ZipFile(ymd, mode = 'w', compression=zipfile.ZIP_LZMA)
	try:
		zipdir(baseFolder,zf)
	finally:
		zf.close()
	os.chdir("..")
	print("Sending images...")
	scp_command = "SSHPASS='al.EX.91.27' sshpass -e scp images/" + ymd + " alext@192.168.0.20:D:\\\\smartGarden\\\\Images"
	os.system(scp_command)
	#os.system("rm " + ymd)
	#os.system("rm -r " + baseFolder)

filename = str(datetime.now()).replace(" ", "-")
dateArray = filename.split('-')
ymd = dateArray[0] + "-" + dateArray[1] + "-" + dateArray[2]
send_folder(ymd)
