import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time

i2c = busio.I2C(board.SCL, board.SDA)
# Soil moisture is address 0x4a
# Light is address 48
soil_ads = ADS.ADS1115(i2c, address=0x4a)

light_ads = ADS.ADS1115(i2c)
light_ads.gain = 2/3
chan1 = AnalogIn(soil_ads, ADS.P0)
chan2 = AnalogIn(light_ads, ADS.P0)

while(True):
    #print("soil value: " + str(chan1.value) + " soil voltage: " + str(chan1.voltage))
    print("light value: " + str(chan2.value) + " light voltage: " + str(chan2.voltage))
    time.sleep(1)