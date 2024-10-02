#!/usr/bin/env python3
"""
Easily generate a plot from the output of tek-control.py

Alec Vercruysse
"""
import argparse
import pdb
import shlex
import sys

import numpy as np
import matplotlib.pyplot as plt

from measurement_tools import interact

si_to_mag = {'y': -24,  # yocto
             'z': -21,  # zepto
             'a': -18,  # atto
             'f': -15,  # femto
             'p': -12,  # pico
             'n': -9,   # nano
             'u': -6,   # micro
             'm': -3,   # mili
             'c': -2,   # centi
             'd': -1,   # deci
             'k': 3,    # kilo
             'M': 6,    # mega
             'G': 9,    # giga
             'T': 12,   # tera
             'P': 15,   # peta
             'E': 18,   # exa
             'Z': 21,   # zetta
             'Y': 24,   # yotta
             }
mag_to_si = {v: k for k, v in si_to_mag.items()}


def main(args):
    arr = np.load(args.infile)
    nchannels = arr.shape[0] - 1
    if args.medfilt != -1:
        assert args.medfilt % 2 == 1
        newsize = arr.shape[-1] - args.medfilt + 1
        newarr = np.zeros((nchannels + 1, newsize))
        cut_amnt = (args.medfilt - 1) // 2
        newarr[0] = arr[0, cut_amnt:-cut_amnt]
        for channel in range(nchannels):
            newarr[channel+1] = np.convolve(
                arr[channel+1], np.ones(args.medfilt),
                mode='valid') / args.medfilt
        arr = newarr
    # check how many samples and decimate if necessary (for speed):
    decimation_factor = int(np.ceil(arr.shape[-1] / 1e5))
    if decimation_factor > 2 and not args.no_decimation:
        print(f'Original data has {arr.shape[-1]} points. ' +
              f'Decimating by {decimation_factor}x.')
        arr = arr[:, ::decimation_factor]
    if args.outfile is None:
        plt.ion()
    # horizontal axis
    time_mag = int(np.floor(np.log10(arr[0, -1]) / 3) * 3)
    plt.xlabel(f'Time [{mag_to_si[time_mag]}s]')

    # vertical axis
    plt.ylabel('Voltage [V]')

    # plot
    plt.plot(arr[0, :, None] * np.ones((1, nchannels)) * (10**-time_mag),
             arr[1:].T)
    plt.grid(visible=True)

    if args.labels:
        plt.legend(args.labels, fancybox=True, shadow=True)
    if args.title:
        plt.title(args.title)
    if args.outfile is not None:
        plt.savefig(args.outfile, bbox_inches='tight', dpi=600,
                    metadata={'invocation': shlex.join(sys.argv[:])})
        print(f"created {args.outfile}")
    else:
        interact.start_interpreter('Interactive interpreter started.')


if __name__ == "__main__":
    print('Running tek-plot.py. Run tek-plot.py -h for help.')
    parser = argparse.ArgumentParser(
        prog='tek-plot.py',
        description='''Start a (potentially interactive) environment to plot a
        .npy file saved by tek-control.py. Decimates if necesssary to
        plot ~1e5 samples.
        ''',
        epilog="Contact: alecfv@berkeley.edu"
    )
    parser.add_argument('infile', help='.npy file containing waveform data.')
    parser.add_argument('--title', '-t', type=str, help='''Title of plot.
    Defaults to <infile>.''')
    parser.add_argument('--labels', '-l',
                        nargs='*', help='''Channel labels.''')
    parser.add_argument('--medfilt', '-m', default=-1,
                        type=int, help='''Apply a median filter of size N
                        to channel data (before potentially undersampling).
                        N must be odd.''')
    parser.add_argument('--no_decimation', '-n', action='store_true',
                        help='''Don't decimate to ~10e5 samples
                        no matter what (slow).''')

    parser.add_argument('--outfile', '-o', default=None, help='''
    Output file name. Generates an interactive matplotlib figure
    if this is not specified.''')
    main(parser.parse_args())
