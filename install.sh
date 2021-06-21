#!/bin/sh
#adafruit libraries
#sudo pip3 install adafruit-circuitpython-ads1x15
#sudo pip3 install flask
#sudo pip3 install Adafruit-Blinka
#python
pip3 install opencv-python
#opencv
sudo apt-get install libcblas-dev
sudo apt-get install libhdf5-dev
sudo apt-get install libhdf5-serial-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install libqt4-test
#paper trail
wget -qO - --header="X-Papertrail-Token: <Token>" \
https://papertrailapp.com/destinations/<Token>/setup.sh | sudo bash
