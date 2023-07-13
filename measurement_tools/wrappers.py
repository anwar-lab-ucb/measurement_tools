"""
Alec Vercruysse
2023-06-27

Factory functins for instruments with 3rd-party python APIs.
TODO refactor, decorators?
"""
import pdb

from measurement_tools import interact
from ThorlabsPM100 import ThorlabsPM100
from pymeasure.instruments.agilent import Agilent33500
from PyTektronixScope import TektronixScope


def OpticalPowerMeter(rm, name=None):
    """
    Factory function to return the ThorlabsPM100 class with similar
    interactivity as the arroyo laser driver.
    Parameters:
    ----------
    rm: pyvisa context manager object.
    name: pyvisa resource name, or none
    """
    if name is None:
        print('Connecting to Thorlabs PM100D:')
        name = interact.get_pyvisa_instr_ID(rm, mytype='OpticalPowerMeter')
    inst = rm.open_resource(name)
    pm = ThorlabsPM100(inst=inst)
    print(f'Successfully connected to {pm.system.sensor.idn}')
    return pm


def Agilent33500BFnGen(rm, name=None):
    """
    Factory function to return the Agilent33500 class with similar
    interactivity as other drivers.

    Parameters:
    ----------
    rm: pyvisa context manager object.
    name: pyvisa resource name, or none
    """
    if name is None:
        print('Connecting to Agilent 33500 Function Generator:')
        name = interact.get_pyvisa_instr_ID(rm, mytype='Agilent33500')
    fngen = Agilent33500(name)
    print(f'Successfully connected to {fngen.ask("*IDN?")}')
    return fngen


def TekScope(rm, name=None):
    """
    Factory function to return the PyTektronixScope class with similar
    interactivity as other drivers. TODO this might be pretty depracated.

    Parameters:
    ----------
    rm: pyvisa context manager object.
    name: pyvisa resource name, or none
    """
    if name is None:
        print('Connecting to Tektronix Oscilloscope:')
        name = interact.get_pyvisa_instr_ID(rm, mytype='TekScope')
    inst = rm.open_resource(name)
    scope = TektronixScope(inst)
    print(f"Successfully connected to {scope.query('*IDN?')}")
    return scope
