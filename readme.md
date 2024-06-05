# Table of Contents

1.  [Install and Setup](#orgcfb76da)
2.  [Scripts](#orgacfb41d)
3.  [Supported Instruments](#org845832a)
    1.  [Arroyo Laser Driver 6310](#orgc3e40c8)
    2.  [ThorLabs PM100D](#org4a3466f)
    3.  [Agilent 33500B Series Waveform Generator](#orgdbeb185)
    4.  [Tektronix 3 Series](#orgaed31b0)


<a id="orgcfb76da"></a>

# Install and Setup

1.  Install this package in your virtual environment with `pip install -e .`
    -   Note this is tested for pyvisa = 1.8
2.  If you get any permission denied error opening USB ports, run:
    -   on Linux: `sudo usermod -a -G dialout <username>`
3.  If having issues correcting to instruments, [pyvisa faq](https://pyvisa.readthedocs.io/en/latest/faq/faq.html#faq-faq) is useful documentation. Try, for example, `pyvisa-info` to make sure the relevant backends seem good to go.
    -   on Debian-based Linux, I needed to install `libusb-dev` apt package to communicate with PM100D. I also had to configure udev rules to give myself access to `/dev/usbtmc0`.
    -   On M1 Mac, I needed to run `brew install libusb`. To get my `pyvisa-info` to be happy when using conda-installed python, I also had to add this symlink: `ln -s /opt/homebrew/lib/libusb-1.0.0.dylib /usr/local/lib/libusb.dylib`. Weird. [see issue.](https://github.com/pyusb/pyusb/issues/355#issuecomment-974726078) The thread also suggests an alternative fix: `export DYLD_LIBRARY_PATH=/opt/homebrew/lib`.

# Quickstart: Connecting to an instrument

This package aims to provide a centralized location (to collect dependencies) and basic wrapper to easily connect to Anwar Lab Instruments with a semi-standardized interface. Other packages do the heavy lifting of defining python interfaces to individual instruments, other than for the Arroyo laser driver.

For instruments whose interfaces are defined outside of this package, as is the case with the optical power meter, the main benefit this package provides other than simplified dependency management is some helper code to identify (and remember) the VISA addresses of the instruments.
Below is an example of connecting to an instrument:

```
import pyvisa
from measurement_tools import OpticalPowerMeter
rm = pyvisa.ResourceManager()
a = OpticalPowerMeter(rm)
help(a)
```

<a id="orgacfb41d"></a>

# Scripts

Scripts automatically install in your path, so you can call them from your shell with tab-autocompletion.
Use e.g. `laser-PIV.py -h` to view the usage of each script. The interactive scripts instantiate an object. In python, call `help(<object name>)` to get a quick reference.
Note that these scripts create a `.measurement_tools` file in your working directory to cache PyVISA instrument IDs to make it easier to associate instruments with their IDs.

-   **laser-PIV.py:** laser optical power & voltage curves stepped at various bias currents. optionally use the f'n gen to pulse the lasers.
-   **agilent33500b-control.py:** interactive control of the F'n gen
-   **laser-control.py:** interactive control of the laser driver
-   **pyvisa-list.py:** simply list discovered pyVisa IDs
-   **tek-control.py:** TODO interactive control of tek scope. backend not working.


<a id="org845832a"></a>

# Supported Instruments


<a id="orgc3e40c8"></a>

## Arroyo Laser Driver 6310

-   This package implements a custom API for this instrument. See `arroyo.py`
    -   [product page](https://www.arroyoinstruments.com/product/6310-combosource-1-amp/)
    -   [PyVISA](https://pyvisa.readthedocs.io/en/latest/index.html) Installation has good debugging info for connecting.
    -   [example arroyo driver with PyVISA](https://github.com/valavanisalex/InstrumentDrivers/blob/master/arroyo.py)
    -   [command manual](https://www.arroyoinstruments.com/wp-content/uploads/2021/01/ArroyoComputerInterfacingManual.pdf)
-   Note that when the python script exits for any reason (including exception), the laser driver is intentionally disabled for safety.
-   TODO sometimes the daemon throws errors on shutdown
-   TODO move to a properties based API rather than explicit getters and setters to be consistent with the other instruments' APIs.


<a id="org4a3466f"></a>

## ThorLabs PM100D

-   API provided by an external package, [ThorlabsPM100](https://pypi.org/project/ThorlabsPM100/). See `scripts/laser-PIV.py` for example usage. [Documentation](https://pythonhosted.org/ThorlabsPM100/thorlabsPM100.html)

<a id="orgdbeb185"></a>

## Agilent 33500B Series Waveform Generator

-   [pymeasure](https://pymeasure.readthedocs.io/en/latest/quick_start.html) provides an API. ([documentation link](https://pymeasure.readthedocs.io/en/latest/api/instruments/agilent/agilent33500.html))
-   tested with development master branch commit de55c6e, it seems that the channel stuff is still unreleased in v0.11.1.
    -   pip installing this package will install the correct version from github.
-   TODO update setup.py dependencies to point to v0.12 when it drops!


<a id="orgaed31b0"></a>

## TODO Tektronix 3 Series
-   Rohan coded a API too ([here](https://github.com/anwar-lab-ucb/tekscope)) for ethernet connection. Consider integration with PyVISA.
