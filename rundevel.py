#!/usr/bin/env python

"""rundevel.py -- script to run current code

Usage: [interpreter] rundevel.py [run|rebot] [options] [arguments]

Examples:
    ./rundevel.py --name Example tests.txt          # run with python
    ./rundevel.py run --name Example tests.txt      # same as above
    jython rundevel.py --name Example tests.txt     # run with jython
    ./rundevel.py rebot --name Example out.xml      # rebot with python
    ipy rundevel.py rebot --name Example out.xml    # rebot with ipy
"""

from os.path import abspath, dirname, exists, join
from os import mkdir, putenv
import sys

if len(sys.argv) == 1:
    sys.exit(__doc__)

curdir = dirname(abspath(__file__))
tmp = join(curdir, 'tmp')
if not exists(tmp):
    mkdir(tmp)

sys.path.insert(0, join(curdir, 'src'))
from robot import run_cli, rebot_cli

if sys.argv[1] == 'rebot':
    runner = rebot_cli
    args = sys.argv[2:]
else:
    runner = run_cli
    args = ['--pythonpath', join(curdir, 'atest', 'testresources', 'testlibs'),
            '--pythonpath', tmp, '--loglevel', 'DEBUG']
    args += sys.argv[2:] if sys.argv[1] == 'run' else sys.argv[1:]

putenv('ROBOT_SYSLOG_FILE', join(tmp, 'syslog.txt'))
runner(['--outputdir', tmp] + args)
