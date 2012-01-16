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
from robot.parsing import TestData, ResourceFile, TestDataDirectory
from robot.parsing.populators import FromFilePopulator


class Tidy(object):

    def __init__(self, **options):
        self._options = options

    def files(self, files):
        for f in files:
            yield self._save_file(f)

    def _save_file(self, path):
        data = self._create_datafile(path)
        output = StringIO()
        data.save(output=output, **self._options)
        return output.getvalue()

    def directory(self, path):
        self._save_recursively(self._create_datafile(path))

    def _save_recursively(self, data):
        init_file = getattr(data, 'initfile', None)
        if init_file or not hasattr(data, 'initfile'):
            data.save(**self._options)
        if os.path.isfile(data.source):
            os.remove(data.source)
        if init_file:
            os.remove(init_file)
        for child in data.children:
            self._save_recursively(child)

    def _create_datafile(self, source):
        if os.path.splitext(os.path.basename(source))[0] == '__init__':
            data = TestDataDirectory()
            data.initfile = source
            FromFilePopulator(data).populate(source)
            return data
        try:
            return TestData(source=source)
        except DataError:
            try:
                return ResourceFile(source=source).populate()
            except DataError:
                raise DataError("Invalid data source '%s'" % source)


def _parse_args():
    parser = utils.ArgumentParser(__doc__)
    return parser.parse_args(sys.argv[1:], help='help', check_args=True)

def main():
    opts, args = _parse_args()
    tidy = Tidy(format=opts['format'], pipe_separated=opts['use-pipes'])
    if not opts['inplace'] or not opts['recursive']:
        for output in tidy.files(args):
            print output
    if opts['recursive']:
        tidy.directory(args[0])


if __name__ == '__main__':
    try:
        main()
    except DataError, err:
        print __doc__
        sys.exit(unicode(err), 1)
    sys.exit(0)
