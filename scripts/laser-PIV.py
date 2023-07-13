#!/usr/bin/env python3
import argparse
import time
import atexit

import pyvisa
import pandas as pd
import numpy as np
from tqdm import tqdm

from measurement_tools import OpticalPowerMeter, LaserDriver, \
    Agilent33500BFnGen
from measurement_tools import spreadsheet, interact


def disable_fn_gen(fngen):
    """
    Make sure to turn Fn Gen off if the script exits at any time!
    """
    fngen.ch[2].output = False


def bias_pulsed(fngen, current):
    """
    Assumes laser driver is in low current mode, so the transfer fn
    is 50mA/V. input units mA.
    """
    v_top = current / 50
    if v_top < 0.01:  # can't go that low. (.5 mA or less, just turn it off)
        fngen.ch[2].output = False
        return
    fngen.ch[2].amplitude = v_top
    fngen.ch[2].offset = v_top / 2
    fngen.ch[2].output = True


def main(args):
    rm = pyvisa.ResourceManager()

    # configure Laser Driver
    i = LaserDriver(rm, Io_max=args.Io_max, Vf_max=args.Vf_max)
    i.set_output_current(0)
    i.enable_output()
    time.sleep(0.5)  # wait to make sure there was no lockout
    assert not i.error

    # configure Power Meter
    p = OpticalPowerMeter(rm)
    p.configure.scalar.power()
    p.sense.power.dc.range.auto = 1
    p.input.pdiode.filter.lpass.state = 1  # low-bandwidth mode
    p.sense.correction.wavelength = args.wavelength

    # optionally configure fn gen
    duty = .5  # 0-1
    freq = 2e3
    if args.pulsed:
        f = Agilent33500BFnGen(rm)
        atexit.register(lambda: disable_fn_gen(f))
        f.ch[2].output = False
        f.ch[2].shape = 'SQU'
        f.ch[2].frequency = freq
        f.ch[2].square_dutycycle = duty * 100  # units of pct
        f.ch[2].amplitude_unit = 'VPP'
        f.ch[2].burst_mode = 'TRIG'            # non-gated
        f.ch[2].trigger_source = 'IMMEDIATE'   # internal trigger

    currents = np.arange(args.start, args.Io_max+1e-9,
                         step=args.step, dtype=int)
    voltages = np.zeros_like(currents, dtype=float)
    powers = np.zeros_like(currents, dtype=float)
    print(f"Sweep currents (mA): {currents}")
    assert interact.confirm("Instruments Configured. Start?")
    for idx, current in tqdm(enumerate(currents), total=len(currents)):
        if args.pulsed:
            bias_pulsed(f, current)
        else:
            i.set_output_current(current)
        time.sleep(.5)  # wait for (Vf) measurements to stabilize.
        voltage = np.mean([i.get_voltage()
                           for _ in range(args.nsamples)])
        power = np.mean([p.read
                         for _ in range(args.nsamples)])
        if i.error:
            print("Exiting early due to error.")
            voltages[idx:] = np.nan
            powers[idx:] = np.nan
            break
        voltages[idx] = voltage
        powers[idx] = power * 1000 * (1 if not args.pulsed else 1 / duty)
        if args.pulsed:
            f.ch[2].output = False
        else:
            i.set_output_current(0)
        time.sleep(.5)
    df = pd.DataFrame(data=np.array([currents, voltages, powers]).T,
                      columns=[f'{args.laserid}_{m}'
                               for m in ['mA', 'V', 'mW']]
                      )
    print("saving...")
    spreadsheet.add_to_spreadsheet(args.filename, df)
    print("done.")


if __name__ == "__main__":
    print('running laser-PIV.py. Run laser-PIV.py -h for help.')
    parser = argparse.ArgumentParser(
        prog='laser-PIV.py',
        description='''Using the Arroyo Laser Driver and Thorlabs PM100D,
        measure the optical power and voltage of the laser at different
        current biases. Stores the results in a spreadsheet.
        ''',
        epilog="Contact: alecfv@berkeley.edu"
    )
    parser.add_argument('laserid',
                        help='''Human readable name of the laser.''')
    parser.add_argument('Io_max', type=int,
                        help='''Maximum current, in mA, to sweep.
                        WARNING! Sets LaserDriver Io_max to this value!'''
                        )
    parser.add_argument('filename',
                        help='''Filename of spreadsheet to put results in.
                        Valid extensions are .csv or .xlsx.
                        Results are appended as columns with the names:
                        <laserid>_mA, <laserid>_mW, <laserid>_V''')
    parser.add_argument('--step', type=int,
                        help='''Step size, in units of integer mA, of sweep.
                        ''')
    parser.add_argument('--start', type=int, default=0,
                        help='''Start mA of sweep. Integer, default 0
                        ''')
    parser.add_argument('--Vf_max', type=float, default=3.2,
                        help='''Maximum forward voltage of the laser.
                        WARNING! Sets LaserDriver vf_max to this value!
                        Default 3.2''')
    parser.add_argument('--nsamples', '-n', type=int, default=20,
                        help='''Number of samples to take at each bias point.
                        Default 20.''')
    parser.add_argument('--wavelength', '-w', type=int, default=650,
                        help='''Wavelenth (for PM100D). Default 650nm.''')
    parser.add_argument('--pulsed', '-p', action='store_true',
                        help='''Measure the laser pulsed at 50pct duty cycle.
                        2KHz Frequency. Uses ch2 of the Agilent33500B.''')

    main(parser.parse_args())
