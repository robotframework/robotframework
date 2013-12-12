#!/usr/bin/env python

from os.path import abspath, dirname, exists, join
from os import mkdir, putenv
import sys

curdir = dirname(abspath(__file__))
tmp = join(curdir, 'tmp')
if not exists(tmp):
    mkdir(tmp)

sys.path.insert(0, join(curdir, 'src'))
from robot import run_cli, rebot_cli

if len(sys.argv) > 1 and sys.argv[1] == 'rebot':
    runner = rebot_cli
    args = sys.argv[2:]
else:
    runner = run_cli
    args = ['--pythonpath', join(curdir, 'atest', 'testresources', 'testlibs'),
            '--pythonpath', tmp, '--loglevel', 'DEBUG'] + sys.argv[1:]

putenv('ROBOT_SYSLOG_FILE', join(tmp, 'syslog.txt'))
runner(['--outputdir', 'tmp'] + args)
