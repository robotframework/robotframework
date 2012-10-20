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

if sys.argv[1] != 'rebot':
    profiled = 'run_cli(sys.argv[1:])'
else:
    profiled = 'rebot_cli(sys.argv[2:])'

results = tempfile.mktemp(suffix='.out', prefix='pybot-profile',
                          dir=join(rootdir, 'tmp'))
cProfile.run(profiled, results)
stats = pstats.Stats(results)
stats.sort_stats('cumulative').print_stats(50)
os.remove(results)
