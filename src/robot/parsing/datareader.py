#  Copyright 2008-2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os

from robot.errors import DataError
from robot import utils

from populator import TestDataPopulator
from htmlreader import HtmlReader
from tsvreader import TsvReader
from txtreader import TxtReader
try:
    from restreader import RestReader
except ImportError:
    def RestReader():
        raise DataError("Using reStructuredText test data requires having "
                        "'docutils' module installed.")


READERS = {'html': HtmlReader, 'htm': HtmlReader, 'xhtml': HtmlReader,
           'tsv': TsvReader , 'rst': RestReader, 'rest': RestReader,
           'txt': TxtReader}


def Reader(path):
    extension = path.split('.')[-1].lower()
    try:
        return READERS[extension]()
    except KeyError:
        raise DataError("No reader found for extension '%s'" % extension)


def read_data(path, datafile):
    if not os.path.isfile(path):
        raise DataError("Data source '%s' does not exist." % path)
    try:
        source = open(path, 'rb')
    except:
        raise DataError(utils.get_error_message())
    try:
        Reader(path).read(source, TestDataPopulator(datafile))
    finally:
        source.close()
