#!/usr/bin/env pytAhon
#
# short_test.py
#
# Run tests for TES-TES shorts and shorts to ground using the pinout PCB
#
# Created by Anthony Corso on 9/8/16.
# Reorganized by Adam Anderson
# 11 October 2016
# adama@fnal.gov


import serial
import time
import csv

Rref = 99500.0

def run(rev, GNDpin=0):
    '''
    Run test for TES-TES shorts and test for shorts to ground.
    
    Parameters
    ----------
    rev : str
        Revision number of MUX PCB ('1' if unmarked, or '2')
    GNDpin : int
        In rev1 of the MUX PCB, there were two possible pins to use
        for ground (0 and 89). In rev2 this argument is irrelevant
        since there is a unique ground pin (90)

    Returns
    -------
    R_dict : dict
        Dictionary of test results
    '''
    connected = False
    ser = serial.Serial('/dev/tty.usbmodem1421', 9600)

    R_dict = {'pin1' : [], 'pin2' : [], 'ADC': [], 'R' : [], 'ADC_gnd': [], 'R_gnd': []}  # good for writing CSV, but a little kludgy given how data comes off the arduino

    time.sleep(1)
    ser.write('TESshorts\n')
    print('Beginning Analysis \r\n ...')
    p = ser.readline()
    while 'end' not in p:
        data = p.rstrip('\n').split(',')
        print('Probing pins %s to %s' % (data[0], data[1]))
        if len(data) == 3:
            R_dict['pin1'].append(int(data[0]))
            R_dict['pin2'].append(int(data[1]))
            R_dict['ADC'].append(float(data[2]))
            ADCval = float(data[2])
            if ADCval != 0:
                Rval = Rref * (1 - ADCval / 1024.0) / (ADCval / 1024.0)
            else:
                Rval = float('Inf')
            R_dict['R'].append(Rval)
        p = ser.readline()

    if rev == '1' and GNDpin == 0:
        ser.write('GNDshorts0\n')
    elif rev == '1' and GNDpin == 89:
        ser.write('GNDshorts1\n')
    elif rev == '2':
        ser.write('GNDshortsRev2\n')
    else:
        return R_dict
    p = ser.readline()
    while 'end' not in p:
        data = p.rstrip('\n').split(',')
        print('Probing pins %s to %s' % (data[0], data[1]))
        if len(data) == 3:
            R_dict['ADC_gnd'].append(float(data[2]))
            ADCval = float(data[2])
            if ADCval != 0:
                Rval = Rref * (1 - ADCval / 1024.0) / (ADCval / 1024.0)
            else:
                Rval = float('Inf')
            R_dict['R_gnd'].append(Rval)
        p = ser.readline()

    ser.close()
    print('Analysis Complete')
    R_dict['info'] = ["Resistance between any two mux pins."]
    return R_dict


def gen_csv(wafer_id, wafer_side, leg, rev):
    if rev == '1':
        if leg % 2 == 1:
            R_dict = run(rev, 89)
        elif leg % 2 == 0:
            R_dict = run(rev, 0)
    elif rev == '2':
        R_dict = run(rev)
            
    fieldnames = ['pin1', 'pin2', 'R', 'R_gnd', 'info']
    max_pin_open = 23
    min_pin_open = 65

    with open('short_test_{0}_{1}_{2}.csv'.format(wafer_id,wafer_side,leg), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pin in R_dict['pin1']:
            info = ''
            if (leg % 2 == 1 and pin <= min_pin_open) or \
               (leg % 2 == 0 and pin >= max_pin_open):
                # check for TES-TES shorts below 1 MOhm
                if pin % 2 == 1 and (R_dict['R'][pin] != float('inf') and R_dict['R'][pin] < 1.e6):
                    info = 'TES-TES short'
                # check for TES opens and resistances >100 kOhm
                elif pin % 2 == 0 and (R_dict['R'][pin] == float('inf') or R_dict['R'][pin] > 1.e5):
                    info = 'TES open'
                if R_dict['R_gnd'][pin] != float('inf') and R_dict['R_gnd'][pin] < 1.e6:
                    info = 'short to GND'
            pin1_real = pin+1
            pin2_real = pin+2
            writer.writerow({'pin1': pin1_real,
                             'pin2': pin2_real,
                             'R': '%2.f' % R_dict['R'][pin],
                             'R_gnd': '%2.f' % R_dict['R_gnd'][pin],
                             'info': info})


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


if __name__ == "__main__":
    import argparse as ap
    P = ap.ArgumentParser(description="Probe SPT wafers for TES-TES shorts and shorts to GND",
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)
    P.add_argument('wafer', metavar='wafer', action='store', default=None,
                   help='wafer name')
    P.add_argument('side', metavar='side', action='store', type=int, default=None,
                   help='side')
    P.add_argument('leg', metavar='leg', action='store', type=int, default=None,
                   help='leg')
    P.add_argument('--rev', metavar='rev', action='store', default='2',
		   help='PCB revision number (1 or 2)')
    args = P.parse_args()

    gen_csv(args.wafer, args.side, int(args.leg), args.rev)
