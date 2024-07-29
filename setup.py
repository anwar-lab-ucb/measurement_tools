"""
Alec Vercruysse
2023-06-27
Required for pip install.
Use pip install -e <path to this dir>
"""
from setuptools import setup, find_packages
print(find_packages())
setup(
    name='anwarlab_measurements',
    version='0.1',
    packages=find_packages(),
    scripts=['scripts/laser-PIV.py',
             'scripts/laser-control.py',
             'scripts/pyvisa-list.py',
             'scripts/agilent33500b-control.py',
             'scripts/tek-control.py',
             'scripts/tek-plot.py'],
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'pyvisa',
        'pyvisa-py',
        'tqdm',
        'zeroconf ',
        'psutil',
        'ThorlabsPM100',
        'openpyxl',
        'pyusb',
        'pymeasure @ git+https://github.com/AlecVercruysse/pymeasure.git',
        'tekscope @ git+https://github.com/anwar-lab-ucb/tekscope.git'
    ]
)
