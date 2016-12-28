import csv
import numpy as np
import re
import pandas as pd

def gen_csv_wafer(wafer_id, wafer_sides=range(1,7), legs=range(1,9)):
    """
    Create a CSV file with wafer yield

    Arguments
    ---------
    wafer_id : string
        Wafer name
    wafer_sides : int or list of ints
        Wafer side(s)
    legs : int or list of ints
        Leg(s) on each wafer side
    """

    wafer_sides = np.atleast_1d(wafer_sides)
    wafer_sides_str = '_'.join([str(x) for x in wafer_sides])

    try:
        wafer_name = re.search('([wW][0-9]+)', wafer_id).group(0).lower()
    except AttributeError as e:
        wafer_name = ''

    data = pd.read_csv('short_test_{}_{}.csv'.format(wafer_id, wafer_sides_str),
                       sep='\t', converters={'status': str, 'Status': str})
    if 'Status' in data:
        data['status'] = data['Status']
        data['side'] = data['Side']
        data['flex_cable'] = data['Flex_cable']

    with open('yield_{}_{}.csv'.format(wafer_id, wafer_sides_str), 'w') as yield_file:
        writer = csv.DictWriter(yield_file, lineterminator='\n', delimiter='\t',
                                fieldnames=['wafer', 'side', 'flex_cable',
                                            'tes_open', 'tes_short', 'ground_short',
                                            'yield', 'yield_frac'])
        writer.writeheader()

        total_open = 0
        total_short = 0
        total_ground = 0
        total_yield = 0
        total_count = 0

        short_idx = data['status'].str.contains('TES-TES short').nonzero()[0]
        short_idx = np.sort(np.append(short_idx, short_idx + 1))
        open_idx = data['status'].str.contains('TES open').nonzero()[0]
        gnd_idx = data['status'].str.contains('short to GND').nonzero()[0]

        empty_idx = (data['bolometer'].str.startswith('129') |
                     data['bolometer'].str.startswith('143')).nonzero()[0]

        for side in wafer_sides:

            side_open = 0
            side_short = 0
            side_ground = 0
            side_yield = 0
            side_count = 0

            for leg in legs:

                onleg = ((data['side'] == side) &
                         (data['flex_cable'] == leg)).nonzero()[0]
                onleg = np.setdiff1d(onleg, empty_idx)

                leg_count = len(onleg)
                if leg_count != 33:
                    print 'Found {} channels on side {} leg {}, expected 33.'.format(
                        leg_count, side, leg)
                    if not leg_count:
                        continue

                is_open = np.in1d(onleg, open_idx)
                is_short = np.in1d(onleg, short_idx)
                is_ground = np.in1d(onleg, gnd_idx)

                leg_open = np.sum(is_open)
                leg_short = np.sum(is_short)
                leg_ground = np.sum(is_ground)
                leg_yield = np.sum(~(is_open | is_short | is_ground))

                # record yield per leg
                leg_yield_frac = leg_yield / float(leg_count)
                side_open += leg_open
                side_short += leg_short
                side_ground += leg_ground
                side_yield += leg_yield
                side_count += leg_count
                writer.writerow({'wafer': wafer_name,
                                 'side': side,
                                 'flex_cable': leg,
                                 'tes_open': leg_open,
                                 'tes_short': leg_short,
                                 'ground_short': leg_ground,
                                 'yield': leg_yield,
                                 'yield_frac': leg_yield_frac})

            # record yield per side
            side_yield_frac = side_yield / float(side_count)
            total_open += side_open
            total_short += side_short
            total_ground += side_ground
            total_yield += side_yield
            total_count += side_count
            writer.writerow({'wafer': wafer_name,
                             'side': side,
                             'flex_cable': 'all',
                             'tes_open': side_open,
                             'tes_short': side_short,
                             'ground_short': side_ground,
                             'yield': side_yield,
                             'yield_frac': side_yield_frac})

        # record total yield
        total_yield_frac = total_yield / float(total_count)
        writer.writerow({'wafer': wafer_name,
                         'side': 'all',
                         'flex_cable': 'all',
                         'tes_open': total_open,
                         'tes_short': total_short,
                         'ground_short': total_ground,
                         'yield': total_yield,
                         'yield_frac': total_yield_frac})

if __name__ == "__main__":

    import argparse as ap

    P = ap.ArgumentParser(description="Tally yield from probe data",
                          formatter_class=ap.ArgumentDefaultsHelpFormatter)
    P.add_argument('wafer', metavar='wafer', action='store', default=None,
                   help='wafer name')
    P.add_argument('-s', '--sides', metavar='side', action='store', type=int,
                   default=range(1,7), nargs='+', choices=range(1,7),
                   help='Wafer side(s). Choices: [1, 2, 3, 4, 5, 6]', )
    P.add_argument('-l', '--legs', action='store', nargs='+', default=range(1,9),
                   type=int, choices=range(1,9), metavar='leg',
                   help='Flex cable leg(s) to analyze')
    args = P.parse_args()

    gen_csv_wafer(args.wafer, args.sides, legs=args.legs)
