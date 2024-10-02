# Install and Setup

1.  Install this package in your virtual environment with `pip install -e .`
    -   Note this is tested for pyvisa = 1.8
2.  If you get any permission denied error opening USB ports, run:
    -   on Linux: `sudo usermod -a -G dialout <username>`
3.  If having issues correcting to instruments, [pyvisa faq](https://pyvisa.readthedocs.io/en/latest/faq/faq.html#faq-faq)
    is useful documentation. Try, for example, `pyvisa-info` to make
    sure the relevant backends seem good to go.
    -   on Debian-based Linux, I needed to install `libusb-dev` apt
        package to communicate with PM100D. I also had to configure
        udev rules to give myself access to `/dev/usbtmc0`.
    -   On M1 Mac, I needed to run `brew install libusb`. To get my
        `pyvisa-info` to be happy when using conda-installed python, I
        also had to add the following symlink: 
        ```ln -s /opt/homebrew/lib/libusb-1.0.0.dylib /usr/local/lib/libusb.dylib```
        Weird. [see issue.](https://github.com/pyusb/pyusb/issues/355#issuecomment-974726078)
        The thread also suggests an alternative fix: `export DYLD_LIBRARY_PATH=/opt/homebrew/lib`.
        - on M1 mac, I was using the `PyVISA-py` backend on MacOS. See the 
          [PyVISA-py documentation](https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/)
        - GPIB support was not working with NI drivers (required by
          even PyVISA-py). A [forum
          post](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/GPIB-USB-HS-no-longer-supported-on-recent-macOS-13/td-p/4313190)
          directed me to the R&S VISA drivers, which claim to support
          MacOS. I eventually gave up on this and used ethernet
          instead.
          

# Quickstart: Connecting to an instrument

This package aims to provide a centralized location (to collect
dependencies) and basic wrapper to easily connect to Anwar Lab
Instruments with a semi-standardized interface. Other packages do the
heavy lifting of defining python interfaces to individual instruments,
other than for the Arroyo laser driver.

For instruments whose interfaces are defined outside of this package,
as is the case with the optical power meter, the main benefit this
package provides other than simplified dependency management is some
helper code to identify (and remember) the VISA addresses of the
instruments.  Below is an example of connecting to an instrument:

```
from measurement_tools import OpticalPowerMeter
a = OpticalPowerMeter()
help(a)
```

Where `OpticalPowerMeter()` is a factory function that returns an
instance of a `ThorlabsPM100` class.

# Scripts

Scripts automatically install in your path, so you can call them from
your shell with tab-autocompletion.  Use e.g. `laser-PIV.py -h` to
view the usage of each script. The interactive scripts instantiate an
object. In python, call `help(<object name>)` to get a quick
reference.  Note that these scripts create a `.measurement_tools` file
in your working directory to cache PyVISA instrument IDs to make it
easier to associate instruments with their IDs.

-   **`laser_PIV.py`** laser optical power & voltage curves stepped at
    various bias currents. optionally use the f'n gen to pulse the
    lasers.
-   **`agilent33500b_control.py`** interactive control of the F'n gen
-   **`laser_control`** interactive control of the laser driver
-   **`pyvisa_list`** simply list discovered pyVisa IDs
-   **`tek_control`** Interactive control of tek scope
-   **`tek_vis`** Quickly plot numpy files saved by `tek_control`

# Supported Instruments
## Arroyo Laser Driver 6310

-   This package implements a custom API for this instrument. See `arroyo.py`
    -   [product page](https://www.arroyoinstruments.com/product/6310-combosource-1-amp/)
    -   [PyVISA](https://pyvisa.readthedocs.io/en/latest/index.html) Installation has good debugging info for connecting.
    -   [example arroyo driver with PyVISA](https://github.com/valavanisalex/InstrumentDrivers/blob/master/arroyo.py)
    -   [command manual](https://www.arroyoinstruments.com/wp-content/uploads/2021/01/ArroyoComputerInterfacingManual.pdf)
-   Note that when the python script exits for any reason (including exception), the laser driver is intentionally disabled for safety.
-   TODO sometimes the daemon throws errors on shutdown
-   TODO move to a properties based API rather than explicit getters and setters to be consistent with the other instruments' APIs.


## ThorLabs PM100D

- API provided by an external package, [ThorlabsPM100](https://pypi.org/project/ThorlabsPM100/). See `scripts/laser-PIV.py` for example usage. [Documentation](https://pythonhosted.org/ThorlabsPM100/thorlabsPM100.html)
- Luke mentioned this might require installing NI-visa to work on windows machines. See [pyvisa documentation](https://pyvisa.readthedocs.io/en/stable/faq/getting_nivisa.html#faq-getting-nivisa).

## Agilent 33500B Series Waveform Generator

-   [pymeasure](https://pymeasure.readthedocs.io/en/latest/quick_start.html) provides an API. ([documentation link](https://pymeasure.readthedocs.io/en/latest/api/instruments/agilent/agilent33500.html))
-   tested with development master branch commit de55c6e, it seems that the channel stuff is still unreleased in v0.11.1.
    -   pip installing this package will install the correct version from github.
-   TODO update setup.py dependencies to point to v0.12 when it drops!


## Agilent E5062A Vector Network Analyzer
Contributed the API to pymeasure.

The instrument has a GPIB connector, but the drivers for the only
GBIP<->USB adapter I found in the lab don't support mac. For this
reason I used an ethernet connection (sending SCPI messages via the
telnet server on the VNA).

1. connect the instrument to your computer via ethernet cable (a
   switch is optional, your adapter probably has auto MDI-X).
2. Configure the IP address of your computer mac to be correct. By
   default the IP address of the VNA is `192.168.2.233` with a subnet
   mask `255.255.255.0`. Manually set the IP address of your adapter to be
   something different on the same subnet (e.g. `192.168.2.234`) with
   the same subnet mask.
    - At this point, `pyvisa-list.py` should show the instrument. If
      not, you can try pinging it's ip address. If that does not work,
      double check its ip address by finding a way to press the
      windows start menu on the VNA (I can do that by opening a random
      network config dialog then the start menu button shows up) >
      Run... > "cmd", then executing `ipconfig`
    - If your mac loses its internet connection, go to system
      settings, "Set Service Order...", and make sure to prioritize
      WiFi over your wired adapter.

## TODO Tektronix 3 Series
-   Rohan coded a API
    ([here](https://github.com/anwar-lab-ucb/tekscope)) for ethernet
    connection. Consider integration with PyVISA.

# Breaking Changes:

- 2024-10-02: bumped version up to 1.0:
  - Migrated from setuptools to non deprecated packaging system
    - renamed all scripts to remove the `.py` and replace hyphens with
      underscores
  - All the wrapper instrument functions no longer require passing in
    your own pyvisa resource manager! This is a breaking change.
