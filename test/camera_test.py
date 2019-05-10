import os
from datetime import datetime

filename = str(datetime.now()).replace(" ", "-")
filename = filename.replace(":","-")
filename = filename.replace(".","-")
print("filename: " + filename)
myCmd = 'fswebcam -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/test/images/' + str(filename) + '.jpg'
scp_command = "scp images/" + filename + ".jpg alex@192.168.0.7:C:\\\\Users\\\\Alex\\\\Desktop\\\\SmartGarden\\\\"
os.system(myCmd)
os.system(scp_command)
