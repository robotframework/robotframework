#!/usr/bin/env python

"""Profiler for Robot Framework `run` and `rebot`.

Usage: profiler.py run|rebot [options] arguments
"""

import cProfile
import pstats
import os
from os.path import abspath, dirname, join
import sys
import tempfile

rootdir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, join(rootdir, 'src'))

from robot.run import run_cli
from robot.rebot import rebot_cli


def profile(profiled):
    results = tempfile.mktemp(suffix='.out', prefix='pybot-profile',
                          dir=join(rootdir, 'tmp'))
    cProfile.run(profiled, results)
    stats = pstats.Stats(results)
    stats.sort_stats('cumulative').print_stats(50)
    os.remove(results)


if __name__ == '__main__':
    try:
        profiled = {'run': 'run_cli(sys.argv[2:])',
                    'rebot': 'rebot_cli(sys.argv[2:])'}[sys.argv[1]]
    except (IndexError, KeyError):
        sys.exit(__doc__)
    profile(profiled)
