#!/usr/bin/env python3
import argparse

import pyvisa
import numpy as np
import matplotlib.pyplot as plt

from measurement_tools import interact, TekScope


def main(args):
    rm = pyvisa.ResourceManager()
    i = TekScope(rm)
    if args.filename is not None:
        x, y = i.read_data_one_channel(channel=args.channel, x_axis_out=True)
        np.save(args.filename, np.hstack((x, y)))
    if args.interactive:
        interact.start_interpreter(
            'Instantiated Scope object \'i\'. Try help(i)')


if __name__ == "__main__":
    print('Running tek-control.py. Run tek-control.py -h for help.')
    parser = argparse.ArgumentParser(
        prog='tek-control.py',
        description='''Start a (potentially interactive) environment to contol
        a Tektronix Scope. Optional flags allow control from the command line.
        ''',
        epilog="Contact: alecfv@berkeley.edu"
    )
    parser.add_argument('--channel', '-c', type=int, default=1,
                        help='Channel to operate on')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Start an interpreter with object instantiated')
    parser.add_argument('--filename', '-f', help='output (numpy binary) file')
    main(parser.parse_args())
