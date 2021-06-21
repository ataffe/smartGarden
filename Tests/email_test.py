from gpiozero import MotionSensor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#import keyboard
import smtplib, ssl


pir = MotionSensor(4)
port = 465 # For SSL
password = "al.EX.91.27"
sender_email = "raspberry.pi.taffe@gmail.com"
receiver_email = input("Please enter the recivers email: ")
#receiver_email = "taffeAlexander@gmail.com"
message = MIMEMultipart("alternative")
message["Subject"] = "Hello From the Raspberry PI"
message["From"] = sender_email
message["To"] = receiver_email
text = """\
 Hi Babe! I got it working! 


This message is sent from Alex's Raspberry pi.
   .~~.   .~~.
  '. \ ' ' / .'
   .~ .~~~..~.
  : .~.'~'.~. :
 ~ (   ) (   ) ~
( : '~'.~.'~' : )
 ~ .~ (   ) ~. ~
  (  : '~' :  ) 
   '~ .~~~. ~'
       '~'
Raspberry Pi

"""
part1 = MIMEText(text, "plain")
message.attach(part1)

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
	server.login("raspberry.pi.taffe@gmail.com", password)
	server.sendmail(sender_email, receiver_email, message.as_string())
	print("Email Sent")
#while True:
#	if(pir.motion_detected):
#		print("Motion Detected")
#	if keyboard.is_pressed('q'):
#		break