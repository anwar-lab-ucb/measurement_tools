#!/usr/bin/env python3
"""
Alec Vercruysse
List discovered pyvisa devices and exit.
"""
import pyvisa
import pprint

if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    pprint.pprint(rm.list_resources())
