#!/usr/bin/env python

#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

Usage:  times2csv.py input-xml [output-csv] [include-items]

This script reads start, end, and elapsed times from all suites, tests and/or
keywords from the given output file, and writes them into an file in
comma-separated-values (CSV) format. CSV files can then be further processed
with spreadsheet programs. If the CSV output file is not given, its name is
got from the input file by replacing the '.xml' extension with '.csv'.

'include-items' can be used for defining which items to process. Possible
values are 'suite', 'test' and 'keyword', and they can be combined to specify
multiple items e.g. like 'suite-test' or 'test-keyword'.

Examples:
  times2csv.py output.xml
  times2csv.py path/results.xml path2/times.csv
  times2csv.py output.xml times.csv test
  times2csv.py output.xml times.csv suite-test
"""

import sys
import os
import csv

from robot.result import ExecutionResult
from robot import utils


def process_file(inpath, outpath, items):
    suite = ExecutionResult(inpath).suite
    outfile = open(outpath, 'wb')
    writer = csv.writer(outfile)
    writer.writerow(['TYPE', 'NAME', 'STATUS', 'START', 'END', 'ELAPSED',
                     'ELAPSED SECS'])
    process_suite(suite, writer, items.lower())
    outfile.close()

def process_suite(suite, writer, items, level=0):
    if 'suite' in items:
        process_item(suite, writer, level, 'Suite')
    if 'keyword' in items:
        for kw in suite.keywords:
            process_keyword(kw, writer, level+1)
    for subsuite in suite.suites:
        process_suite(subsuite, writer, items, level+1)
    for test in suite.tests:
        process_test(test, writer, items, level+1)

def process_test(test, writer, items, level):
    if 'test' in items:
        process_item(test, writer, level, 'Test', 'suite' not in items)
    if 'keyword' in items:
        for kw in test.keywords:
            process_keyword(kw, writer, level+1)

def process_keyword(kw, writer, level):
    if kw is None:
        return
    process_item(kw, writer, level, kw.type.capitalize())
    for subkw in kw.keywords:
        process_keyword(subkw, writer, level+1)

def process_item(item, writer, level, item_type, long_name=False):
    indent = '' if level == 0 else ('|  ' * (level-1) + '|- ')
    name = (item.longname if long_name else item.name).encode('UTF-8')
    elapsed = utils.elapsed_time_to_string(item.elapsedtime)
    writer.writerow([indent+item_type, name, item.status, item.starttime,
                     item.endtime, elapsed, item.elapsedtime/1000.0])


if __name__ == '__main__':
    if not (2 <= len(sys.argv) <= 4) or sys.argv[1] in ('--help', '-h'):
        print __doc__
        sys.exit(1)
    inxml = sys.argv[1]
    try:
        outcsv = sys.argv[2]
    except IndexError:
        outcsv = os.path.splitext(inxml)[0] + '.csv'
    try:
        items = sys.argv[3]
    except IndexError:
        items = 'suite-test-keyword'
    process_file(inxml, outcsv, items)
    print os.path.abspath(outcsv)
