#!/usr/bin/env python
import time
import serial

ser = serial.Serial(
    port='/dev/ttyS0',
    # port='/dev/ttyACM0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1000
)

data ='00001111'

while 1:
    ser.write(str(data).encode())
    time.sleep(1)