#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")

fswebcam -r 1280x720 /home/pi/Desktop/smartGarden/smartGarden/images/$DATE.jpg
