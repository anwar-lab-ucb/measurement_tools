"""
Alec Vercruysse
2023-06

USB Control of Arroyo Laser Driver.
Settings taken from the now out-of-date arroyo.py in
https://github.com/valavanisalex/InstrumentDrivers

TODO:
No sort of control/handling of temperature limits/TEC settings.
This has only been tested with the bare die lasers. The settings
need to be preset to not turn off laser if e.g. TEC is off.

TODO:
Consider refactoring so that gettable and settable things
are properties rather than methods.
"""
from datetime import datetime, timedelta
import time
import threading
import atexit
import sys

import pyvisa
from pyvisa import constants

from measurement_tools import interact


class LaserDriver:
    def __init__(self, rm, Io_max=None, Vf_max=None, name=None):
        """
        Prompts interactively if name is not provided.
        Io_max: maximum forward current in mA
        Vf_max: maximum forward voltage in Volts.
        """
        self.rm = rm
        self.idn = None
        if name is None:
            print('Connecting to Laser Driver:')
            name = interact.get_pyvisa_instr_ID(rm, mytype='LaserDriver')
        self.name = name
        self.instr = self.rm.open_resource(self.name)
        self.instr.baud_rate = 38400
        self.instr.timeout = 500
        self.instr.write_termination = '\n'
        self.instr.send_end = True
        self.instr.data_bits = 8
        self.instr.stop_bits = constants.StopBits['one']
        self.instr.parity = constants.Parity['none']
        try:
            self.idn = self.instr.query('*IDN?')
        except pyvisa.errors.VisaIOError:
            # Weirdly, it errors out once and works the second time.
            self.idn = self.instr.query('*IDN?')
            print("\nClear any errors that appear on the " +
                  "Laser Driver Screen and disregard!!!!")
        print(f'Successfully connected to {self.idn}')
        self.instr_lock = threading.Lock()
        self.error = False
        self.watchdog = threading.Thread(target=self._laser_error_watchdog,
                                         daemon=True)
        self.watchdog.start()
        atexit.register(self.close)
        if Io_max is not None:
            self.set_current_limit(Io_max)
        if Vf_max is not None:
            self.set_voltage_limit(Vf_max)

    def set_current_limit(self, limit, confirm=True):
        """
        in mA.
        """
        if confirm:
            with self.instr_lock:
                old_limit = self.query_reg('LASER:LIMIT:LDI?')
            if limit > old_limit:
                response = interact.confirm(
                    f'Raise Laser Io limit from {old_limit} to {limit} mA?')
                if not response:
                    return
        with self.instr_lock:
            self.instr.write('LASER:LIMIT:LDI ' + str(limit))
        print(f'Set Laser Io limit to {limit} mA.')

    def set_voltage_limit(self, limit, confirm=True):
        """
        in V.
        """
        if confirm:
            with self.instr_lock:
                # pdb.set_trace()
                old_limit = self.query_val('LASER:LIMIT:LDV?')
            if limit > old_limit:
                response = interact.confirm(
                    f'Raise Laser Vf limit from {old_limit} to {limit} V?')
                if not response:
                    return
        with self.instr_lock:
            self.instr.write('LASER:LIMIT:LDV ' + str(limit))
        print(f'Set Laser Vf limit to {limit} V.')

    def set_output_current(self, mA):
        '''
        Set output current in mA.
        '''
        with self.instr_lock:
            I_max = self.query_reg('LASER:LIMIT:LDI?')
        assert mA <= I_max
        with self.instr_lock:
            self.instr.write("LASER:LDI " + str(mA))

    def get_voltage(self):
        '''
        Get the measured voltage in V
        '''
        with self.instr_lock:
            retval = self.query_val("LASER:LDV?")
        return retval

    def enable_output(self):
        self.set_enable(1)

    def disable_output(self):
        self.set_enable(0)

    def set_enable(self, enable, asynchronous=False):
        """
        TODO can we catch interlock errors?
        """
        with self.instr_lock:
            self.instr.write(f'LASER:OUTPUT {1 if enable else 0}')
        if not asynchronous:
            self._wait_until_condition(laser_output=enable)

    def query_reg(self, query):
        """
        example inputs: 'LASER:COND?', '*ESE?'.
        Need to aquire a lock first!
        """
        return int(self.query_val(query))

    def query_val(self, query):
        """
        Need to aquire a lock first!
        """
        return self.instr.query_ascii_values(query)[0]

    def _laser_error_watchdog(self):
        laser_cond_bits = {
            0: "Current Limit",
            1: "Voltage Limit",
            4: 'Interlock Error',
            7: 'Open Circuit',
            8: 'Output Shorted'
        }
        with self.instr_lock:
            # clear error register (e.g. from prev. run)
            self.query_reg('LASER:EVENT?')
        while True:  # self._run_watchdog.is_set():
            time.sleep(1)
            with self.instr_lock:
                val = self.query_reg('LASER:EVENT?')
            for bit, issue in laser_cond_bits.items():
                if val & (1 << bit):
                    self.error = True
                    # Exception would stop watchdog
                    print(f'Watchdog: Laser {issue}!!')

    def _wait_until_condition(self, laser_output=None,
                              timeout=5000):
        """
        Timeout in ms.
        """
        start = datetime.now()
        if laser_output is not None:
            query = 'LASER:COND?'
            bit = 10  # Output On bit in Laser Condition Status Register
            target = laser_output
        else:
            raise NotImplementedError
        done = False
        while not done:
            with self.instr_lock:
                val = self.query_reg(query)
            if (val & (1 << bit)) == (target << bit):
                done = True
            elif (datetime.now() - start) / timedelta(
                    milliseconds=1) > timeout:
                raise TimeoutError("Laser Driver timed out " +
                                   f"waiting for condition {laser_output=}" +
                                   f" ({query}={val})")

    def close(self):
        """
        TODO maybe this should use the __enter__/__exit__ pattern.
        Registering with atexit seems to work for now.
        """
        print(f"Closing {self.name}: {self.idn}")
        try:
            self.disable_output()
            with self.instr_lock:
                self.instr.close()
        except pyvisa.errors.InvalidSession:
            raise Exception(
                'PyVISA session closed before Laser Driver could be closed.')
