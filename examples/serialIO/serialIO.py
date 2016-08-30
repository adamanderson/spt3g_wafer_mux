import serial
import time

ser = serial.Serial('/dev/tty.usbserial-ADAPGZQw0')
time.sleep(2)
ser.write(b'hello\n')

#time.sleep(1)

data = ser.readline()
print(data)

ser.close()
