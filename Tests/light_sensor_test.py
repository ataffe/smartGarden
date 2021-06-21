import board
import busio
import adafruit_tsl2561
import time

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_tsl2561.TSL2561(i2c)
sensor.gain = 0

while True:
    print('Lux: {}'.format(sensor.lux))
    print('Broadband: {}'.format(sensor.broadband))
    print('Infrared: {}'.format(sensor.infrared))
    print('gain: {}'.format(sensor.gain))
    print('Luminosity: {}\n'.format(sensor.luminosity))
    time.sleep(1)
