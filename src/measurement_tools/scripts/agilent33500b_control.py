#!/usr/bin/env python3
import argparse

import pyvisa

from measurement_tools import interact, Agilent33500BFnGen


def run(args):
    rm = pyvisa.ResourceManager()
    i = Agilent33500BFnGen(rm)
    ch = i.channels[args.channel]
    if args.enable and args.disable:
        raise ValueError('Cannot both disable and enable the channel at once.')
    if args.shape:
        ch.shape = args.shape
    if args.frequency:
        ch.frequency = args.frequency
    if args.offset:
        ch.offset = args.offset
    if args.units:
        ch.amplitude_unit = args.unit
    if args.amplitude:
        ch.amplitude = args.amplitude
    if args.enable:
        ch.output = True
    if args.disable:
        ch.output = False
    if args.interactive:
        interact.start_interpreter(
            'Instantiated Agilent33500BFnGen object \'i\'. Try help(i)')


def main():
    print('Running agilent33500b-control.py. ' +
          'Run laser-agilent33500b-control.py -h for help.')
    parser = argparse.ArgumentParser(
        prog='agilent33500b-control.py',
        description='''Start a (potentially interactive) environment to contol
        the Agilent33500B Function Generator. Optional flags allow control from
        the command line.''',
        epilog="Contact: alecfv@berkeley.edu"
    )
    parser.add_argument('--channel', '-c', type=int, default=1,
                        help='Channel to set setting for. ' +
                        'Can only control one channel at a time.')
    parser.add_argument('--shape', '-s', choices=[
        'SIN', 'SQU', 'TRI', 'RAMP',
        'PULS', 'PRBS', 'NOIS', 'ARB', 'DC'],
                        help='Waveform Shape.')
    parser.add_argument('--frequency', '-f', type=float,
                        help='Frequency (1uHz -> 120MHz)')
    parser.add_argument('--offset', '-o', type=float,
                        help='Voltage offset, must be positive, ' +
                        'max = (Vmax-voltage)/2')
    parser.add_argument('--amplitude', '-a', type=float,
                        help='10mV -> 10V, depending on output impedance. ' +
                        'See --units flag. If --units is unspecified,' +
                        'it will stick to the current setting (default Vpp).')
    parser.add_argument('--units', type=float,
                        help='10mV -> 10V, depending on output impedance. ' +
                        'Vpp default, but see --units flag')
    parser.add_argument('--enable', '-e', action='store_true',
                        help='Turn output on for the specified channel. ' +
                        'All other configuration options set first.')
    parser.add_argument('--disable', '-d', action='store_true',
                        help='Turn output off for the specified channel.')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Enter interacftive interpreter.')
    run(parser.parse_args())
