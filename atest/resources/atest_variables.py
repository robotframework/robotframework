from os.path import abspath, dirname, join, normpath
import locale
import os
import subprocess

import robot


__all__ = ['ROBOTPATH', 'ROBOT_VERSION', 'DATADIR', 'SYSTEM_ENCODING',
           'CONSOLE_ENCODING']


ROBOTPATH = dirname(abspath(robot.__file__))
ROBOT_VERSION = robot.version.get_version()
DATADIR = normpath(join(dirname(abspath(__file__)), '..', 'testdata'))

# FIXME: Always use locale.getpreferredencoding when atests are run on Py 3.6!
if os.name == 'nt':
    SYSTEM_ENCODING = locale.getpreferredencoding(False)
    # FIXME: Add encoding when running atests on Py 3.6
    cp = subprocess.check_output('chcp', shell=True).split()[-1]
    CONSOLE_ENCODING = 'cp' + cp
else:
    SYSTEM_ENCODING = 'UTF-8'
    CONSOLE_ENCODING = locale.getdefaultlocale()[-1]
