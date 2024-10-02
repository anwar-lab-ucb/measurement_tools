#!/usr/bin/env python3
import argparse

import numpy as np
# import matplotlib.pyplot as plt

from measurement_tools import interact, TekScope
# from tekscope import raw


def run(args):
    i = TekScope(None)
    if args.filename is not None:
        vs = []
        wfms = i.retrieve_all_waveforms()
        t = None
        for channel in args.channel:
            wfm = wfms.get(f'CH{channel}')
            if wfm is not None:
                if t is None:
                    t = np.array(wfm.time())
                vs += [np.array(wfm.voltage())]
            else:
                print(f'Warning: No channel {channel} data.')
        np.save(args.filename, np.vstack((t, *vs)))
    if args.reset:
        i.send_raw_command('*RST')  # reset scope
    if args.mode:
        mode = 'NORMal' if args.mode == 'normal' else 'AUTO'
        i.send_raw_command(f':TRIGger:A:MODE {mode}')
    if args.hscale:
        i.send_raw_command(f':HORIZONTAL:SCALE {args.hscale}')
    if args.hpos:
        i.send_raw_command(f':HORIZONTAL:POSITION {args.hpos}')
    if args.interactive:
        interact.start_interpreter(
            'Instantiated Scope object \'i\'. Try help(i)')


def main():
    print('Running tek-control.py. Run tek-control.py -h for help.')
    parser = argparse.ArgumentParser(
        prog='tek-control.py',
        description='''Start a (potentially interactive) environment to contol
        a Tektronix Scope. Optional flags allow control from the command line.
        ''',
        epilog="Contact: alecfv@berkeley.edu"
    )
    parser.add_argument('--channel', '-c', type=int, default=[1, 2, 3, 4],
                        nargs='+',
                        help='''Integers from 1-4, channel(s) to operate on.
                        Defaults to all.''')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Start an interpreter with object instantiated')
    parser.add_argument('--reset', '-r', action='store_true',
                        help='Reset the Oscilloscope settings to known state')
    parser.add_argument('--mode', '-m', action='store',
                        choices=['auto', 'normal'],
                        help='Set trigger mode.')
    parser.add_argument('--hpos', action='store', type=float,
                        help='Set horizontal scroll position, between 0-100.')
    parser.add_argument('--hscale', action='store', type=float,
                        help='Set horizontal scale in units of s/div.')

    parser.add_argument('--filename', '-f', help='''output (numpy binary) file.
    The shape of the numpy array is (<1 + # channels>, <nsamples>), where
    arr[0,:] is time and arr[1:,:] are the channel voltage data.''')
    main(parser.parse_args())
