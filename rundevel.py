#!/usr/bin/env python

"""rundevel.py -- script to run the current Robot Framework code

Usage: [interpreter] rundevel.py [run|rebot] [options] [arguments]

Options and arguments are same as Robot Framework itself accepts. Sets some
command line options and environment variables to ease executing tests under
the `atest/testdata` directory. Writes all outputs into `tmp` directory in
the project root.

Examples:
    ./rundevel.py --name Example tests.robot          # Run with default Python
    ./rundevel.py run --name Example tests.robot      # Same as the above
    ./rundevel.py rebot --name Example out.robot      # Rebot
"""

from os.path import abspath, dirname, exists, join
import os
import sys


if len(sys.argv) == 1:
    sys.exit(__doc__)

curdir = dirname(abspath(__file__))
src = join(curdir, 'src')
tmp = join(curdir, 'tmp')
tmp2 = join(tmp, 'rundevel')
if not exists(tmp):
    os.mkdir(tmp)
if not exists(tmp2):
    os.mkdir(tmp2)

os.environ['ROBOT_SYSLOG_FILE'] = join(tmp, 'syslog.txt')
if 'ROBOT_INTERNAL_TRACES' not in os.environ:
    os.environ['ROBOT_INTERNAL_TRACES'] = 'true'
os.environ['TEMPDIR'] = tmp2          # Used by tests under atest/testdata
if 'PYTHONPATH' not in os.environ:    # Allow executed scripts to import robot
    os.environ['PYTHONPATH'] = src
else:
    os.environ['PYTHONPATH'] = os.pathsep.join([src, os.environ['PYTHONPATH']])

sys.path.insert(0, src)
from robot import run_cli, rebot_cli

if sys.argv[1] == 'rebot':
    runner = rebot_cli
    args = sys.argv[2:]
else:
    runner = run_cli
    args = ['--pythonpath', join(curdir, 'atest', 'testresources', 'testlibs'),
            '--pythonpath', tmp,
            '--loglevel', 'DEBUG']
    args += sys.argv[2:] if sys.argv[1] == 'run' else sys.argv[1:]

runner(['--outputdir', tmp] + args)
