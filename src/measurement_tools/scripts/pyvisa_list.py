#!/usr/bin/env python3
"""
Alec Vercruysse
List discovered pyvisa devices and exit.
"""
import pyvisa
import pprint


def main():
    rm = pyvisa.ResourceManager()
    pprint.pprint(rm.list_resources())


if __name__ == '__main__':
    main()
