# Smart Garden 
# [![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) [![ForTheBadge powered-by-electricity](http://ForTheBadge.com/images/badges/powered-by-electricity.svg)](http://ForTheBadge.com)

### This is my DIY project to automate my indoor garden using a raspberry pi 3b. There is a soil moisture sensor, a lux sensor and a temperature sensor for input. There is a DC water pump for the watering the garden and an led grow light to supplement sunlight for the plants. I currently have filebeat running on the raspberry pi sending log data to logstash which filters the logs and then sends the data to elasticsearch running on a PC. Kibana is used to visualize the data from the sensor for further development.

### My goal is to optimize the growth of the plants. I would like to water based on the soil moisture instead of watering at set intervals and to provide suplemental light based on the amount of natural light. Currently I am watering based on the soil moisture sensor but the grow light is on a set interval. The soil temperature is monitored via a water proof temperature sensor which is burried in the soil about 4 inches below the surface.

###### Kibana Dashboard
This is the kibana dashboard I use to monitor the sensor data in almost real time. (Refreshes every 1 second)
![alt text](https://raw.github.com/ataffe/smartGarden/master/images/Dashboard1.PNG)
![alt text](https://raw.github.com/ataffe/smartGarden/master/images/Dashboard2.PNG)

###### The Actual Setup
![alt text](https://raw.github.com/ataffe/smartGarden/master/infographic/IMG_6855.jpg)

###### Time Lapse Video of the strawberries
A time lapse using opencv and a camera mounted on the pot. This is old I am working on a new one.
[![GARDEN](https://img.youtube.com/vi/t3zazeLUzj0/0.jpg)](https://www.youtube.com/watch?v=t3zazeLUzj0&feature=youtu.be)

[![alt text](https://raw.github.com/ataffe/smartGarden/master/infographic/Elastic_Stack_Logo.jpg)](https://www.elastic.co/) 
[![alt text](https://raw.github.com/ataffe/smartGarden/master/infographic/RPI_Logo.png)](https://www.raspberrypi.org/)
[![alt text](https://raw.github.com/ataffe/smartGarden/master/images/circuitPython.png)](https://circuitpython.org/)
