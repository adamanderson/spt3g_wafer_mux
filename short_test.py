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
    voltage_dict = {'pin1' : [], 'pin2' : [], 'voltage' : []}
    counter = 0
    print('Beginning Analysis \r\n ...')
    while len(voltage_dict['pin1'])<31:
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
                voltage_dict['pin1'].append(channel1)
                voltage_dict['pin2'].append(channel2)
                if voltage != 'inf':
                    voltage_dict['voltage'].append(voltage)
                else:
                    voltage_dict['voltage'].append('open')
            #print(voltage_dict)
            #print('running')
        if counter != 3:
            counter += 1
        else:
            counter = 0
    ser.write(b'0\r\n')
    ser.close()
    print('Analysis Complete')
    voltage_dict['info'] = ["Voltage between any two mux pins."]
    return voltage_dict
    #meme = ser.readline()
    #meme = meme.decode("utf-8")
    #print(meme)

"""
    Write dict {'pin1', 'pin2', 'voltage'}
    perhaps write two separate dicts - one for odds, one for evens?
"""

def gen_csv():
    import csv
    voltage_dict = run()
    with open('short_test.csv', 'w') as csvfile:
        fieldnames = ['pin1', 'pin2', 'voltage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for pin in voltage_dict['pin1']:
            pin = int(float(pin))
            writer.writerow({'pin1': voltage_dict['pin1'][pin], 'pin2': voltage_dict['pin2'][pin], 'voltage': voltage_dict['voltage'][pin]})


def gen_pdf():

    """
        Requires pydfmux
        
    """
    import pydfmux
    from pydfmux.core.utils.rail_monitoring import RailMonitor
    from pydfmux.core.utils.restructured_text import ReStructuredText
    from pydfmux.core.utils import save_returns, pfb_gains
    dict = run()
    shortlist = []
    for pin1 in dict:
        for pin2 in dict[pin1]:
            if not dict[pin1][pin2] == 'inf':
                shortlist.append[ [ (pin1, pin2, dict[pin1][pin2]) ] ]
    savepath = 'blah' #something
    savename = 'blah' #something
    rst_path = os.path.join(savepath, 'rst_docs')
    out_path = os.path.join(plot_path, savename)
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    if not os.path.exists(rst_path):
        os.makedirs(rst_path)
    rst_path = os.path.join(rst_path, savename + '.rst')
    rst_file = open(rst_path, 'w')

    rest = ReStructuredText(rst_file)
    rest.add_header('Medusa Cable Short Test')
    if len(shortlist) == 0:
        rest.add_section_header('There are no shorts!')
    else:
        rest.add_section_header('List of shorts [pin1, pin2, voltage readout]')
        rest.add_table(shortlist)
    rst_file.close()
    os.system("rst2pdf '{0}' -o '{1}'".format(rst_path, os.path.join(savepath, savename + '.pdf')))