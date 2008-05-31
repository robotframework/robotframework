#!/usr/bin/env python

#  Copyright 2008 Nokia Siemens Networks Oyj
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


"""Robot Framework Start/End/Elapsed Time Reporter

Usage:  times2csv.py input-xml [output-csv]

This script reads start, end, and elapsed times from all suites, tests
and keywords from the given output file, and writes them into an file
in comma-separated-values (CSV) format. CSV files can then be further
processed with spreadsheet programs. If the CSV output file is not
given, its name is got from the input file by replacing the '.xml'
extension with '.csv'.
"""

import sys
import os
import csv

from robot.output import TestSuite


def process_file(inpath, outpath):
    suite = TestSuite(inpath)
    outfile = open(outpath, 'wb')
    writer = csv.writer(outfile, delimiter=';')
    writer.writerow(['TYPE','NAME','STATUS','START','END','ELAPSED','ELAPSED SECS'])
    process_suite(suite, writer)
    outfile.close()

def process_suite(suite, writer, level=0):
    process_item(suite, writer, level, 'Suite')
    for kw in suite.setup, suite.teardown:
        process_keyword(kw, writer, level+1)
    for subsuite in suite.suites:
        process_suite(subsuite, writer, level+1)
    for test in suite.tests:
        process_test(test, writer, level+1)

def process_test(test, writer, level):
    process_item(test, writer, level, 'Test')
    for kw in [test.setup] + test.keywords + [test.teardown]:
        process_keyword(kw, writer, level+1)
    
def process_keyword(kw, writer, level):
    if kw is None:
        return
    if kw.type in ['kw', 'set', 'repeat']:
        kw_type = 'Keyword'
    else:
        kw_type = kw.type.capitalize()
    process_item(kw, writer, level, kw_type)
    for subkw in kw.keywords:
        process_keyword(subkw, writer, level+1)
    
def process_item(item, writer, level, item_type):
    if level == 0:
        indent = ''
    else:
        indent = '|  ' * (level-1) + '|- '
    row = [ indent+item_type, item.name, item.status, item.starttime,
            item.endtime, item.elapsedtime, item.elapsedmillis/1000.0 ]
    writer.writerow(row)


if __name__ == '__main__':
    if not (2 <= len(sys.argv) <= 3) or '--help' in sys.argv:
        print __doc__
        sys.exit(1)
    inxml = sys.argv[1]
    if len(sys.argv) == 2:
        outcsv = os.path.splitext(inxml)[0] + '.csv'
    else:
        outcsv = sys.argv[2]
    process_file(inxml, outcsv)
    print os.path.abspath(outcsv)
