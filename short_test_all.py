#!/usr/bin/env python
#
# short_test_all.py
#
# Run tests for TES-TES shorts and shorts to ground using the pinout PCB
#
# Created by Anthony Corso on 9/8/16.
# Reorganized by Adam Anderson
# 11 October 2016
# adama@fnal.gov
#
# Further reorganized by Sasha Rahlin
# 18 November 2016
# arahlin@fnal.gov


import serial
import time
import csv
import numpy as np

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

    # good for writing CSV, but a little kludgy given how data comes off the arduino
    R_dict = {'pin1' : [], 'pin2' : [], 'ADC': [], 'R' : [], 'ADC_gnd': [], 'R_gnd': []}

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

def run_leg(rev, leg):
    """
    Run short checks on the given leg.
    """
    max_pin_open = 23
    min_pin_open = 65

    if str(rev) == '1':
        if leg % 2 == 1:
            R_dict = run(rev, 89)
        elif leg % 2 == 0:
            R_dict = run(rev, 0)
    elif str(rev) == '2':
        R_dict = run(rev)

    for k,v in R_dict.items():
        if k == 'info':
            continue
        R_dict[k] = np.asarray(v)

    n_open = 0
    n_short = 0
    n_gnd = 0
    n_ok = 0

    R_dict['status'] = []
    for pin in R_dict['pin1']:
        info = ''
        if (leg % 2 == 1 and pin <= min_pin_open) or \
           (leg % 2 == 0 and pin >= max_pin_open):
            # check for TES-TES shorts below 1 MOhm
            if pin % 2 == 1 and (~np.isinf(R_dict['R'][pin]) and R_dict['R'][pin] < 1.e6):
                info = 'TES-TES short'
                n_short += 1
            # check for TES opens and resistances >100 kOhm
            elif pin % 2 == 0 and (np.isinf(R_dict['R'][pin]) or R_dict['R'][pin] > 1.e5):
                info = 'TES open'
                n_open += 1
            elif pin % 2 == 0:
                n_ok += 1
            # check for shorts to ground
            if ~np.isinf(R_dict['R_gnd'][pin]) and R_dict['R_gnd'][pin] < 1.e6:
                info = 'short to GND'
                n_gnd += 1
        R_dict['pin1'][pin] = pin + 1
        R_dict['pin2'][pin] = pin + 2
        R_dict['status'].append(info)

    print 'Results for leg {}:'.format(leg)
    print n_short, 'TES-TES shorts'
    print n_open, 'TES opens'
    print n_gnd, 'shorts to ground'
    print n_ok, 'good connections'

    return R_dict

def wafer_bolo_info(wafer_side=None):
    '''
    Returns full channel bookkeeping information for channels on a wafer. Note
    that all wafers are identical, so this function has no arguments

    Borrowed wholesale from hwm_tools.py

    Parameters
    ----------
    wafer_side : int, optional
        If supplied, only return mapping for the given side.

    Returns
    -------
    mapping : dict
        Generic channel mapping information for a full wafer or one side
    '''
    mapping = {'Pixel': np.array([], dtype=np.int32),
               'Band': np.array([]),
               'Pol': np.array([]),
               'bolometer': np.array([]),
               'Side': np.array([]),
               'Flex_cable': np.array([]),
               'LC_ind': np.array([]),
               'ZIF_odd': np.array([])}
    hex_sides = [1,2,3,4,5,6]

    # version 2 LC chip
    # if zifs are pointed down, and chip is above them, this is reading the
    # wiring from left to right
    forder_chip=np.array([43, 10, 52, 53, 11, 44, 31, 21, 64, 65, 20, 32, 42,
                          19, 67, 66, 18, 41, 30, 13, 56, 57, 12, 29, 39,  6, 59, 58,  7, 40, 27, 17,
                          63, 62, 16, 28, 38,  1, 51, 50,  0, 37, 26,  2, 48, 49,  3, 25, 35, 14, 60,
                          61, 15, 36, 23,  9, 55, 54,  8, 24, 34,  5, 47, 46,  4, 33], dtype=np.int32)

    #this table is the pixel to wafer wiring.  each columm is a side of the hex
    #1-6 according to wendy's wiring layout.
    wafer_wiring=np.array([
        [262, 271, 145,	10,  1,   127],
        [252, 260, 144,	20,  12,  128],
        [229, 235, 142,	43,  37,  130],
        [202, 206, 140,	70,  66,  132],
        [171, 173, 138,	101, 99,  134],
        [172, 156, 119,	100, 116, 153],
        [263, 261, 126,	9,   11,  146],
        [253, 249, 125,	19,  23,  147],
        [242, 236, 124,	30,  36,  148],
        [230, 222, 123,	42,  50,  149],
        [217, 207, 122,	55,  65,  150],
        [264, 250, 108,	8,   22,  164],
        [254, 237, 107,	18,  35,  165],
        [203, 191, 121,	69,  81,  151],
        [243, 223, 106,	29,  49,  166],
        [231, 208, 105,	41,  64,  167],
        [265, 238, 91,	7,   34,  181],
        [255, 224, 90,	17,  48,  182],
        [188, 174, 120,	84,  98,  152],
        [218, 192, 104,	54,  80,  168],
        [244, 209, 89,	28,  63,  183],
        [266, 225, 75,	6,   47,  197],
        [256, 210, 74,	16,  62,  198],
        [204, 175, 103,	68,  97,  169],
        [232, 193, 88,	40,  79,  184],
        [189, 157, 102,	83,  115, 170],
        [267, 211, 60,	5,   61,  212],
        [245, 194, 73,	27,  78,  199],
        [257, 195, 59,	15,  77,  213],
        [219, 176, 87,	53,  96,  185],
        [205, 158, 86,	67,  114, 186],
        [268, 196, 46,	4,   76,  226],
        [246, 178, 58,	26,  94,  214],
        [258, 179, 45,	14,  93,  227],
        [233, 177, 72,	39,  95,  200],
        [220, 159, 71,	52,  113, 201],
        [269, 180, 33,	3,   92,  239],
        [234, 160, 57,	38,  112, 215],
        [247, 161, 44,	25,  111, 228],
        [259, 162, 32,	13,  110, 240],
        [136, 163, 21,	2,   109, 251],
        [270, 137, 118,	117, 135, 154],
        [155, 139, 85,	82,  133, 187],
        [190, 141, 56,	51,  131, 216],
        [221, 143, 31,	24,  129, 241],
        [248, -1,  -1,  -1,  -1,  -1]], dtype=np.int32)	# Side 1 reads out an extra pixel.

    for side in hex_sides:
        pixel_list=np.array([],dtype=np.int32)
        band_list=np.array([],dtype=np.int32)
        pol_list=np.array([],dtype=np.int32)
        # First six bolos on each side not read out:
        cable_list=np.array([-1,-1,-1,-1,-1,-1], dtype=np.int32)
        lcind_list=np.array([-1,-1,-1,-1,-1,-1], dtype=np.int32)
        zifodd_list=np.array([-1,-1,-1,-1,-1,-1], dtype=np.int32)

        for jj in range(len(wafer_wiring[:,0])): # For each pixel on a side:
            # Pixel labels for 6 bolos
            pixel_list = np.append(pixel_list, np.ones(6,dtype=np.int32)*wafer_wiring[jj,side-1])
            # Order the bolos are read out in, by band
            band_list=np.append(band_list,np.array([150,90,220,220,90,150], dtype=np.int32))
            # Order the bolos are read out in, by pol. 0= x, 1=y
            pol_list=np.append(pol_list,np.array([1,0,0,1,1,0]))

        for jj in range(8): # For each flex cable leg:
            # Flex cable labels for bolos, 33 bolos per leg.
            cable_list=np.append(cable_list,np.ones(33,dtype=np.int32)*(jj+1))
            if np.mod(jj,2)==0:
                zifodd_list = np.append(zifodd_list, np.arange(1,66,2))
            elif np.mod(jj,2)==1:
                zifodd_list = np.append(zifodd_list, np.arange(25,90,2))
        # Extra pixel (last six bolos) on Side 1 not read out.
        cable_list=np.append(cable_list, np.ones(6,dtype=np.int32)-1)
        zifodd_list=np.append(zifodd_list, np.ones(6,dtype=np.int32)-1)

        for jj in range(4): # Each side of the wafer is read out by 4 LC combs
            # Frequency index labels for all bolos on a side
            lcind_list=np.append(lcind_list,forder_chip)
        # Extra pixel (last six bolos) on Side 1 not read out.
        lcind_list=np.append(lcind_list,np.ones(6,dtype=np.int32)-2)

        mapping['Pixel'] = np.append(mapping['Pixel'], np.array(pixel_list))
        mapping['Band'] = np.append(mapping['Band'], np.array(band_list))
        mapping['Pol'] = np.append(mapping['Pol'], np.array(pol_list))
        mapping['bolometer'] = np.append(
            mapping['bolometer'],
            np.array(['%d.%s.%s' % info for info in
                      zip(pixel_list, band_list,
                          np.array(np.array(['x','y'])[pol_list]))]))
        mapping['Side'] = np.append(mapping['Side'], np.ones(cable_list.shape) * side)
        mapping['Flex_cable'] = np.append(mapping['Flex_cable'], np.array(cable_list))
        mapping['LC_ind'] = np.append(mapping['LC_ind'], np.array(lcind_list))
        mapping['ZIF_odd'] = np.append(mapping['ZIF_odd'], np.array(zifodd_list))

    # select only one side
    if wafer_side in hex_sides:
        idx = np.where(mapping['Side'] == wafer_side)[0]

        for k, v in mapping.items():
            mapping[k] = v[idx]

    return mapping

def gen_csv_side(wafer_id, wafer_side, rev):
    """
    Create a CSV file for one side of the wafer.

    Arguments
    ---------
    wafer_id : string
        Wafer name
    wafer_side : int
        Wafer side
    rev : string
        PCB revision
    """

    wafer = wafer_bolo_info(wafer_side)

    fieldnames = ['Side', 'Flex_cable', 'ZIF_odd', 'bolometer',
                  'R', 'R_neighbor', 'R_ground_1', 'R_ground_2', 'Status']

    with open('short_test_{}_{}.csv'.format(wafer_id, wafer_side), 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for leg in xrange(1,9):
            try:
                raw_input('\n\nConnect leg {} and press ENTER to analyze. Ctrl+D to exit. '.format(leg))
            except EOFError:
                break

            # measure
            R_dict = run_leg(rev, leg)

            # get wafer mapping for this leg
            wafer_idx = np.where((wafer['Side'] == wafer_side) &
                                 (wafer['Flex_cable'] == leg))[0]
            wafer_data = [wafer[k][wafer_idx] for k in
                          ['ZIF_odd', 'bolometer']]

            for zif, bolo in zip(*wafer_data):

                # match resistance data to mapping
                if zif in R_dict['pin1']:
                    idx = np.where(R_dict['pin1'] == zif)[0][0]
                    R = '%.2f' % R_dict['R'][idx]
                    R_gnd = '%.2f' % R_dict['R_gnd'][idx]
                    status = R_dict['status'][idx]

                    if zif + 1 in R_dict['pin1']:
                        idx = np.where(R_dict['pin1'] == zif + 1)[0][0]
                        R_neighbor = '%.2f' % R_dict['R'][idx]
                        R_gnd_2 = '%.2f' % R_dict['R_gnd'][idx]
                    else:
                        R_neighbor = ''
                        R_gnd_2 = ''
                else:
                    R = ''
                    R_gnd = ''
                    R_neighbor = ''
                    R_gnd_2 = ''
                    status = ''

                # write
                writer.writerow({'Side': wafer_side,
                                 'Flex_cable': leg,
                                 'ZIF_odd': zif,
                                 'bolometer': bolo,
                                 'R': R,
                                 'R_neighbor': R_neighbor,
                                 'R_ground_1': R_gnd,
                                 'R_ground_2': R_gnd_2,
                                 'Status': status})

if __name__ == "__main__":
    import argparse as ap
    P = ap.ArgumentParser(description="Probe SPT wafers for TES-TES shorts and shorts to GND",
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)
    P.add_argument('wafer', metavar='wafer', action='store', default=None,
                   help='wafer name')
    P.add_argument('side', metavar='side', action='store', type=int, default=None,
                   help='side')
    P.add_argument('--rev', metavar='rev', action='store', default='2', choices=['1','2'],
		   help='PCB revision number (1 or 2)')
    args = P.parse_args()

    gen_csv_side(args.wafer, args.side, args.rev)
