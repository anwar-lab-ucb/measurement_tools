#!/usr/bin/env python3
import argparse

import pyvisa

from measurement_tools import interact, LaserDriver


def run(args):
    rm = pyvisa.ResourceManager()
    i = LaserDriver(rm)
    if args.io_max is not None:
        print(f"Setting current limit to {args.io_max} mA")
        i.set_current_limit(args.io_max)
    if args.current is not None:
        print(f"Setting current to {args.current} mA")
        i.set_output_current(args.current)
    if args.enable:
        print("Enabling output...")
        i.enable_output()
        print("Done.")
    if args.interactive:
        interact.start_interpreter(
            'Instantiated LaserDriver object \'i\'. Try help(i)')


def main():
    print('Running laser-control.py. Run laser-control.py -h for help.')
    parser = argparse.ArgumentParser(
        prog='laser-control.py',
        description='''Start a (potentially interactive) environment to contol
        the laser. Optional flags allow control from the command line.
        ''',
        epilog="Contact: alecfv@berkeley.edu"
    )
    parser.add_argument('--enable', '-e', action='store_true',
                        help='''Enable laser output (executed last). Note that
                        since the laser driver turns off as soon as the script
                        controlling it exits (for safety), you need to start
                        this script in interactive mode to have the laser
                        stay on.''')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='''Start in interactive mode
                        (with a LaserDriver object instantiated)''')
    parser.add_argument('--io_max', '-m', type=int,
                        help='''set Io_max of laser driver''')
    parser.add_argument('--current', '-c', type=int,
                        help='''Set output current (does not raise Io_lim)''')
    run(parser.parse_args())
