# Alec Vercruysse
# 2024-07-31
#
# Utility functions for the lab VNA (agilentE5062A) that aren't fit for the
# pymeasure class

import skrf.network
import numpy as np


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
    for i, (tr, parameter) in enumerate(zip(
            channel.traces.values(),
            ['S11', 'S12', 'S21', 'S22'])):
        tr.parameter = parameter
        tr.activate()
        channel.trace_format = 'POL'
        re, im = channel.data
        s_matrix[:, i] = re + 1j * im
    return skrf.network.Network(
        f=freqs,
        s=s_matrix.reshape(-1, 2, 2),
        z0=50
    )
