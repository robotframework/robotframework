import locale
import os
import subprocess
from datetime import datetime, timedelta
from os.path import abspath, dirname, join, normpath

import robot


__all__ = ['ROBOTPATH', 'ROBOT_VERSION', 'DATADIR', 'SYSTEM_ENCODING',
           'CONSOLE_ENCODING', 'datetime', 'timedelta']


ROBOTPATH = dirname(abspath(robot.__file__))
ROBOT_VERSION = robot.version.get_version()
DATADIR = normpath(join(dirname(abspath(__file__)), '..', 'testdata'))

SYSTEM_ENCODING = locale.getpreferredencoding(False)
# Python 3.6+ uses UTF-8 internally on Windows. We want real console encoding.
if os.name == 'nt':
    output = subprocess.check_output('chcp', shell=True, encoding='ASCII',
                                     errors='ignore')
    CONSOLE_ENCODING = 'cp' + output.split()[-1]
else:
    CONSOLE_ENCODING = locale.getlocale()[-1]
