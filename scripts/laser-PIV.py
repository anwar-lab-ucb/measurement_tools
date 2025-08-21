#!/usr/bin/env python3
import argparse
import time
import atexit
import pdb

import pyvisa
import pandas as pd
import numpy as np
from tqdm import tqdm

from measurement_tools import OpticalPowerMeter, LaserDriver, \
    Agilent33500BFnGen, TekScope
from measurement_tools import spreadsheet, interact


def disable_fn_gen(fngen):
    """
    Make sure to turn Fn Gen off if the script exits at any time!
    """
    fngen.channels[2].output = False


def set_tint(f, tint_s):
    """
    Set integration time on fn gen.
    Used in integration mode only.
    """
    if tint_s > 0:
        print(f.channels[2].pulse_period)
        duty_cycle = 100 * tint_s / f.channels[2].pulse_period
        f.channels[2].pulse_dutycycle = duty_cycle
        f.channels[2].output = True
    else:
        f.channels[2].output = False


def bias_pulsed(fngen, current):
    """
    Assumes laser driver is in low current mode, so the transfer fn
    is 50mA/V. input units mA.
    """
    v_top = current / 50
    if v_top < 0.01:  # can't go that low. (.5 mA or less, just turn it off)
        fngen.channels[2].output = False
        return
    fngen.channels[2].amplitude = v_top
    fngen.channels[2].offset = v_top / 2
    fngen.channels[2].output = True


def main(args):
    rm = pyvisa.ResourceManager()

    # configure Power Meter
    p = OpticalPowerMeter()
    p.configure.scalar.power()
    p.sense.correction.wavelength = args.wavelength
    if not args.integration_mode:  # default
        p.sense.power.dc.range.auto = 1
        p.input.pdiode.filter.lpass.state = 1  # low-bandwidth mode
    else:
        # The actual range is dependent on the wavelength setting...
        p.sense.power.dc.range.upper = 0.01    # >=10mW
        p.input.pdiode.filter.lpass.state = 0  # hi-bandwidth mode

    # optionally configure fn gen
    assert not (args.pulsed and args.integration_mode)
    if args.pulsed:
        duty = .5  # 0-1
        freq = 2e3
        f = Agilent33500BFnGen()
        atexit.register(lambda: disable_fn_gen(f))
        f.channels[2].output = False
        f.channels[2].shape = 'SQU'
        f.channels[2].frequency = freq
        f.channels[2].square_dutycycle = duty * 100  # units of pct
        f.channels[2].amplitude_unit = 'VPP'
        f.channels[2].burst_mode = 'TRIG'            # non-gated
        f.channels[2].trigger_source = 'IMMEDIATE'   # internal trigger
    if args.integration_mode:
        f = Agilent33500BFnGen()
        atexit.register(lambda: disable_fn_gen(f))
        f.channels[2].output = False
        f.channels[2].amplitude_unit = 'VPP'
        f.channels[2].trigger_source = 'BUS'
        f.channels[2].burst_mode = 'TRIGGERED'  # all cycles after trigger?
        f.channels[2].burst_ncycles = 1
        f.channels[2].shape = 'PULS'
        f.channels[2].pulse_transition = 9e-9   # 8.4ns is min.
        f.ext_trig_out = True
        f.write('OUTPut:TRIGger:SLOPe POS')
        f.write('OUTPut:TRIGger:SOURCe CH2')
        set_tint(f, 50e-3)  # 50 ms.
        f.channels[2].output = True
        f.trigger()  # try one trigger, sometimes theres a spurious pulse
        f.channels[2].output = False

    # optionally configure scope
    if args.integration_mode:
        s = TekScope(host_id="169.254.8.189")
        s.send_raw_command('*RST')  # reset scope'
        s.send_raw_command(':SELect:CH1 1')    # trig
        s.send_raw_command('CH1:SCALE 200E-3')  # 200mV/div (20mV = 1 mA)
        s.send_raw_command(':SELect:CH4 1')
        s.send_raw_command('CH4:SCALE 500E-3')   # 2V max
        s.send_raw_command(':TRIGger:A:TYPe EDGE')
        s.send_raw_command(':TRIGger:A:EDGE:SOUrce CH1')
        s.send_raw_command(':TRIGger:A:LOWerthreshold:CH1 0.5')
        s.send_raw_command(':TRIGger:A:EDGE:SLOpe RISE')
        s.send_raw_command(':TRIGger:A:MODE NORMal')
        s.send_raw_command(':HORIZONTAL:SCALE 1E-2')  # 10ms / div
        s.send_raw_command(':HORIZONTAL:RECOrdlength 1000000')  # 1M so fs=10 MS/s
        s.send_raw_command(':HORIZONTAL:POSITION 10')  # trig pos @ 10% f.s.
        time.sleep(3)  # TODO this is just to make sure the scope has time to reset

    # configure Laser Driver
    i = LaserDriver(rm, Io_max=args.Io_max, Vf_max=args.Vf_max)
    i.set_output_current(0)
    i.enable_output()
    time.sleep(0.5)  # wait to make sure there was no lockout
    assert not i.error



    currents = np.arange(args.start, args.Io_max+1e-9,
                         step=args.step, dtype=int)
    voltages = np.zeros_like(currents, dtype=float)
    powers = np.zeros_like(currents, dtype=float)
    print(f"Sweep currents (mA): {currents}")
    assert interact.confirm("Instruments Configured. Start?")
    for idx, current in tqdm(enumerate(currents), total=len(currents)):
        if args.pulsed or args.integration_mode:
            bias_pulsed(f, current)
        else:
            i.set_output_current(current)

        # get power in integration mode!
        if args.integration_mode:
            s.send_raw_command('CLEAR')
            # clear prev measurement to ensure we are measuring the next
            # trigger.
            time.sleep(.5)
            f.trigger()
            time.sleep(1)
            wfm = s.retrieve_waveform('CH4')
            if wfm is None:
                print('Error: scope did not trigger')
                powers[idx:] = np.nan
                voltages[idx:] = np.nan
                break
            t, v = np.array(wfm.time()), np.array(wfm.voltage())
            # map 2V to range:
            real_range = p.sense.power.dc.range.upper / 1.1
            power = np.mean(
                v[np.logical_and(t > 0,
                                 t <= 50e-3)] / 2 * real_range)
            if power < 0:
                print('''Error: Negative Optical Power recorded.
                (TODO: Is the scope code detecting when
                the waveform is not recorded/scope didn't trigger?)''')
                pdb.set_trace()
            # still in integration mode, now measure Vf
            i.set_output_current(current)
        # all modes:
        time.sleep(.5)  # wait for power to stabilize.
        if not args.integration_mode:
            power = np.mean([p.read
                             for _ in range(args.nsamples)])
        voltage = np.mean([i.get_voltage()
                           for _ in range(args.nsamples)])
        if i.error:
            print("Exiting early due to error.")
            voltages[idx:] = np.nan
            powers[idx:] = np.nan
            break
        voltages[idx] = voltage
        powers[idx] = power * 1000 * (1 if not args.pulsed else 1 / duty)
        if args.pulsed:
            f.channels[2].output = False
        else:
            i.set_output_current(0)
        time.sleep(.5)  # I hope this is enough cool-off time...
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
                        2KHz Frequency. Uses ch2 of the Agilent33500B to
                        modulate the laser driver. Note! Do not use this,
                        since the Vf reported by the laser driver is not
                        accurate. Cannot be run with -i.''')
    parser.add_argument('--integration_mode', '-i', action='store_true',
                        help='''At each current step, first measure the
                        average optical power over 50ms.
                        Then, turn off modulation
                        and measure the voltage using the DC mode of the
                        laser driver. This results in accurate Vf measurements
                        while being able to control the on time of the laser.
                        Cannot be run with -p.
                        TODO: manual intervention required! trig out (and
                        maybe other fn gen params? needs to be set manually)
                        The scpi commands were not working for me.

                        Experimental setup:
                        - ch2 of the agilent33500b modulating the laser driver.
                        - EXT TRIG on the back of the agilent33500b connected
                        to ch1 of the scope.
                        - analog out of the PM100D connected to ch4 of the tek.
                        ''')

    main(parser.parse_args())
