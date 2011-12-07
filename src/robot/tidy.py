"""robot.tidy: Clean up and change format of Robot Framework test data files.

Usage: python -m robot.tidy [options] input

Options:
 -f --format TXT|HTML|TSV  Output file format. If omitted, format of the input
                           file is used.
 -o --output path          Output file. If omitted, basename of the input file
                           is used. If extension is included,
                           overrides format given with --format option.
 -P --use-pipes            Use pipe (`|`) as cell separator in txt format.
 -h --help                 Show this help.

 Examples:

 python -m robot.tidy -f txt mytests.html  # Creates mytets.txt
"""

import sys

from robot import utils, DataError
from robot.parsing import TestData

def _exit(message, status):
    print message
    if status:
        print __doc__
    sys.exit(status)

def _parse_args():
    parser = utils.ArgumentParser(__doc__)
    try:
        return parser.parse_args(sys.argv[1:], help='help', check_args=True)
    except DataError, err:
        _exit(unicode(err), 1)

def _create_datafile(source):
    try:
        return TestData(source=source)
    except DataError, err:
        _exit("Invalid data source '%s': %s" % (source, unicode(err)), 1)


if __name__ == '__main__':
    opts, args = _parse_args()
    datafile = _create_datafile(args[0])
    outpath = datafile.save(path=opts['output'], format=opts['format'],
                            pipe_separated=opts['use-pipes'])
    _exit("%s -> %s" % (args[0], outpath), 0)
