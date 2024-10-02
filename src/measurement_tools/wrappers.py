"""
Alec Vercruysse
2023-06-27

Factory functins for instruments with 3rd-party python APIs.
TODO refactor, decorators?
"""
import pyvisa

from measurement_tools import interact
from ThorlabsPM100 import ThorlabsPM100
from pymeasure.instruments.agilent import Agilent33500, AgilentE5062A
from tekscope import Oscilloscope, raw


def OpticalPowerMeter(name=None):
    """
    Factory function to return the ThorlabsPM100 class with similar
    interactivity as the arroyo laser driver.

    Parameters:
    ----------
    rm: pyvisa context manager object.
    name: pyvisa resource name, or none
    """
    print('Connecting to Thorlabs PM100D:')
    rm = pyvisa.ResourceManager()
    if name is None:
        name = interact.get_pyvisa_instr_ID(rm, mytype='OpticalPowerMeter')
    inst = rm.open_resource(name)
    pm = ThorlabsPM100(inst=inst)
    print(f'Successfully connected to {pm.system.sensor.idn}')
    return pm


def Agilent33500BFnGen(name=None, **kwargs):
    """
    Factory function to return the Agilent33500 class with similar
    interactivity as other drivers.

    Parameters:
    ----------
    rm: pyvisa context manager object.
    name: pyvisa resource name, or none
    """
    print('Connecting to Agilent 33500 Function Generator:')
    rm = pyvisa.ResourceManager()
    if name is None:
        name = interact.get_pyvisa_instr_ID(rm, mytype='Agilent33500')
    fngen = Agilent33500(name, **kwargs)
    print(f'Successfully connected to {fngen.ask("*IDN?")}')
    return fngen


def AgilentE5062AVNA(name=None, **kwargs):
    """
    Factory function to return the AgilentE5062A class with similar
    interactivity as other drivers.

    Parameters:
    ----------
    rm: pyvisa context manager object.
    name: pyvisa resource name, or none
    """
    print('Connecting to Agilent E5602A VNA:')
    rm = pyvisa.ResourceManager()
    if name is None:
        name = interact.get_pyvisa_instr_ID(rm, mytype='AgilentE5602A')
    vna = AgilentE5062A(name, **kwargs)
    print(f'Successfully connected to {vna.ask("*IDN?")}')
    return vna


def TekScope():
    """
    Factory function to return the Oscilloscope class with similar
    interactivity as other drivers.

    TODO this does not yet use the pyVISA backend. rm is a dummy argument.
    need to connect with ethernet cable, and somehow have the scope
    automatically pick it's own IP address.
    """
    print('Connecting to Tektronix Oscilloscope:')
    scope = Oscilloscope(host="169.254.8.194")
    scope.send_raw_command('*IDN?')
    resp = raw.query_ascii(scope.soc).decode('ascii')
    print(f"Successfully connected to {resp}")
    return scope
