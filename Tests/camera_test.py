import os
import zipfile
from datetime import datetime
import cv2

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def create_folder():
    filename = str(datetime.now()).replace(" ", "-")
    dateArray = filename.split('-')
    ymd = dateArray[0] + "-" + dateArray[1] + "-" + dateArray[2]
    try:
        os.mkdir("/home/pi/Desktop/smartGarden/smartGarden/test/images/" + ymd)
    except FileExistsError:
        pass
    finally:
        return ymd

def send_folder(ymd):
    print("Zipping File...")
    baseFolder = ymd
    ymd = baseFolder + ".zip"
    os.chdir("images")
    zf = zipfile.ZipFile(ymd, mode = 'w', compression=zipfile.ZIP_LZMA)
    try:
        zipdir(baseFolder,zf)
    	#zf.write("images/" + ymd,"dir\\images"/ + ymd, compress_type= zipfile.ZIP_DEFLATED)
    finally:
    	zf.close()
    print("Sending images...")
    scp_command = "SSHPASS='al.EX.91.27' sshpass -e scp " + ymd + " alext@192.168.0.20:D:\\\\smartGarden\\\\Images"
    os.system(scp_command)
    os.system("rm " + ymd)
    os.system("rm -r " + baseFolder)
    os.chdir("..")
    print(os.listdir())

def take_pics(ymd, number=1, sharpness=1):
    for x in range(number):
        print("Taking image " + str(x + 1) + " out of " + str(number))
        filename = str(datetime.now()).replace(" ", "-")
        filename = filename.replace(":","-")
        filename = filename.replace(".","-")
        filename = filename + ".jpg"
        #resolution 1280x720
        vid_cap = cv2.VideoCapture(0)
        vid_cap.set(3, 1280)
        vid_cap.set(4, 720)
        if not vid_cap.isOpened():
            raise Exception("could not open video device")
            
        for x in range(10):
            ret, frame = vid_cap.read()
            
        cv2.imwrite("/home/pi/Desktop/smartGarden/smartGarden/test/images/" + ymd + "/" + str(filename), frame)
        vid_cap.release()
        #myCmd = 'fswebcam -q -i 0 -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/test/images/' + ymd + "/" + str(filename)
        #os.system(myCmd)
        

    

ymd = create_folder()
take_pics(ymd, 2, 5)
#take_pics(ymd, 5, 5)
#take_pics(ymd, 5, 6)
send_folder(ymd)



