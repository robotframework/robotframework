"""robot.tidy: Clean up and change format of Robot Framework test data files.

Usage: python -m robot.tidy [options] inputfile
   or: python -m robot.tidy --inplace [options] inputfile [more input files]
   or: python -m robot.tidy --recursive [options] directory

Options:
 -i --inplace    Tidy given file(s) so that original file(s) are overwritten
                 (or removed, if the format is changed) When this option is
                 used, it is possible to give multiple input files. Examples:
                 robotidy.py --inplace tests.html
                 robotidy.py --inplace --format txt *.html
 -r --recursive  Process given directory recursively. Files in the directory
                 are processed in place similarly as when '--inplace'
                 option is used.
 -f --format txt|html|tsv
                 Output file format. If omitted, format of the input
                 file is used.
 -p --use-pipes  Use pipe (`|`) as cell separator in txt format.
 -h --help       Show this help.

 Examples:

 python -m robot.tidy -f txt mytests.html  # Creates mytets.txt
"""
import os
import sys
from StringIO import StringIO

from robot import utils
from robot.errors import DataError
from robot.parsing import TestCaseFile, ResourceFile, TestDataDirectory
from robot.parsing.populators import FromFilePopulator

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
    if os.path.splitext(os.path.basename(source))[0] == '__init__':
        data = TestDataDirectory()
        data.initfile = source
        FromFilePopulator(data).populate(source)
        return data
    try:
        return TestCaseFile(source=source).populate()
    except DataError, err:
        try:
            return ResourceFile(source=source).populate()
        except DataError:
            _exit("Invalid data source '%s': %s" % (source, unicode(err)), 1)


if __name__ == '__main__':
    opts, args = _parse_args()
    datafile = _create_datafile(args[0])
    if not opts['inplace'] or not opts['recursive']:
        output = StringIO()
        datafile.save(output=output, format=opts['format'],
                      pipe_separated=opts['use-pipes'])
        print output.getvalue()
    _exit("", 0)
