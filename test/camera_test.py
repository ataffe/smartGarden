import os
import zipfile
from datetime import datetime

filename = str(datetime.now()).replace(" ", "-")
filename = filename.replace(":","-")
filename = filename.replace(".","-")
filename = filename + ".jpg"
print("filename: " + filename)
myCmd = 'fswebcam -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/test/images/' + str(filename)
os.system(myCmd)
zf = zipfile.ZipFile("images/" + filename + ".zip", mode = 'w')
try:
	zf.write("images/" + filename, compress_type= zipfile.ZIP_DEFLATED)
finally:
	zf.close()
os.system("rm images/*.jpg")

scp_command = "scp images/" + filename + ".zip alext@192.168.0.20:C:\\\\Users\\\\ALEXT\\\\OneDrive\\\\Desktop\\\\SmartGarden\\\\"
os.system(scp_command)
