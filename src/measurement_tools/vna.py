# Alec Vercruysse
# 2024-07-31
#
# Utility functions for the lab VNA (agilentE5062A) that aren't fit for the
# pymeasure class.

import skrf.network
import numpy as np
import measurement_tools
from pyvisa.errors import VisaIOError
from pathlib import Path


def construct_network(channel):
    """Given a channel of an AgilentE5062A, measure all S-parameters of the
    network and return an skrf.network.Network object.

    Assumes the sweep settings have been set.

    TODO does changing the trace value restart a sweep/clear averaging? Should
    we be waiting for averaging in this method?

    """
    freqs = channel.frequencies
    s_matrix = np.empty((freqs.size, 4), dtype=np.complex64)
    channel.visible_traces = 4
    for i, (tr, parameter) in enumerate(
        zip(channel.traces.values(), ["S11", "S12", "S21", "S22"])
    ):
        tr.parameter = parameter
        tr.activate()
        channel.trace_format = "POL"
        re, im = channel.data
        s_matrix[:, i] = re + 1j * im
    return skrf.network.Network(f=freqs, s=s_matrix.reshape(-1, 2, 2), z0=50)


def monitor_vna_err_queue(routine):
    """Double check the the VNA threw no errors. Requires the VNA object to be
    the first argument to the wrapped funtion

    """

    def new_routine(vna, *args, **kwargs):
        vna.clear()
        routine(vna, *args, **kwargs)
        code, msg = vna.pop_err()
        if code != 0:
            raise IOError(f"VNA threw error code {code}: {msg}")

    return new_routine


@monitor_vna_err_queue
def setup_vna_for_cal(vna, fstart=300e3, fstop=100e6, f_IF=1e3):
    """Requires a new cal when this is called! (and it changes settings)"""
    ch = vna.channels[1]  # choose channel 1
    ch.start_frequency = fstart  # 300 kHz (lower bound)
    ch.stop_frequency = fstop  # 100 MHz default
    ch.scan_points = 1601  # max?
    ch.IF_bandwidth = f_IF  # 1 kHz default, compromise for speed
    vna.attenuation = 0
    vna.power = 0
    input("VNA set up for calibration. Continue?")


def wait_for_complete(vna, attempt=1, max_attempts=20):
    """
    Wait a long time for the synchronization bit.
    """
    try:
        vna.complete
    except VisaIOError:
        if attempt == max_attempts:
            raise
        else:
            wait_for_complete(vna, attempt=attempt + 1, max_attempts=max_attempts)


@monitor_vna_err_queue
def init_measurement(vna):
    ch = vna.channels[1]
    ch.visible_traces = 4
    for i, (tr, parameter) in enumerate(
        zip(ch.traces.values(), ["S11", "S12", "S21", "S22"])
    ):
        tr.parameter = parameter


@monitor_vna_err_queue
def measure_and_save_touchstone(vna, fname, averaging=10):
    init_measurement(vna)  # ensure we're measuring everything
    ch = vna.channels[1]
    ch.averages = averaging
    ch.averaging_enabled = True
    ch.trigger_continuous = False
    vna.trigger_source = "BUS"
    vna.abort()
    ch.restart_averaging()
    for _ in range(averaging):
        ch.trigger_initiate()  # arm channel 1
        vna.trigger_single()  # send a trigger
        wait_for_complete(vna)
    network = measurement_tools.vna.construct_network(vna.ch_1)
    network.name = Path(fname).name
    network.write_touchstone(fname)
    return network
