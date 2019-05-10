import os
from datetime import datetime

filename = str(datetime.now()).replace(" ", "-")
filename = filename.replace(":","-")
filename = filename.replace(".","-")
print("filename: " + filename)
myCmd = 'fswebcam -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/test/images/' + str(filename) + '.jpg'
os.system(myCmd)
