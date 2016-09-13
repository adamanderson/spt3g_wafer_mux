#!/bin/sh

#  IOSerial.py
#  
#
#  Created by Anthony Corso on 9/8/16.
#

def run():
    import serial
    import time
    connected = False
    ser = serial.Serial('/dev/cu.usbmodem1411', 9600)
    #while not connected:
    #serin = ser.read()
    #connected = True
    #print(serin)
    #connected = True
    ser.write(b'1\r\n')
        #while ser.read() == '1':
    voltage_dict = {}
    counter = 0
    while len(voltage_dict)<64:
        p = ser.readline()
        p = p.decode("utf-8")
        #print(p)
        if not p == '':
            if counter == 0:
                channel1 = p.split('\r\n')[0]
                #voltage_dict[channel1]
            elif counter == 1:
                channel2 = p.split('\r\n')[0]
                #voltage_dict['channel_1']['channel_2'] = channel2
            elif counter == 2:
                voltage = p.split('\r\n')[0]
                #channel1 = '{0}'.format(channel1)
                #channel2 = '{0}'.format(channel2)
                try:
                    voltage_dict[channel1]
                except KeyError:
                    voltage_dict[channel1] = {}
                voltage_dict[channel1][channel2] = voltage
            #print(voltage_dict)
        if counter != 3:
            counter += 1
        else:
            counter = 0
    ser.write(b'0\r\n')
    ser.close()
    voltage_dict['info'] = ["Voltage between any two mux pins; ideally, all should be 'inf'
                            ."]
    return voltage_dict
    #meme = ser.readline()
    #meme = meme.decode("utf-8")
    #print(meme)