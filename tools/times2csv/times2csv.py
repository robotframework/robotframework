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

Usage:  times2csv.py input-xml [output-csv] [include-items]

This script reads start, end, and elapsed times from all suites, tests
and/or keywords from the given output file, and writes them into an file
in comma-separated-values (CSV) format. CSV files can then be further
processed with spreadsheet programs. If the CSV output file is not
given, its name is got from the input file by replacing the .xml
extension with .csv. Include-items can be used for defining which 
items are written. Possible include values are suite, test and keyword and 
those are separated with -. For example when suites' and test cases' 
information is needed include-items needs to be suite-test.
"""

import sys
import os
import csv

from robot.output import TestSuite


def process_file(inpath, outpath, items):
    suite = TestSuite(inpath)
    outfile = open(outpath, 'wb')
    writer = csv.writer(outfile)
    writer.writerow(['TYPE','NAME','STATUS','START','END','ELAPSED','ELAPSED SECS'])
    process_suite(suite, writer, items.lower())
    outfile.close()

def process_suite(suite, writer, items, level=0):
    if 'suite' in items:
        process_item(suite, writer, level, 'Suite')
    if 'keyword' in items:
        for kw in suite.setup, suite.teardown:
            process_keyword(kw, writer, level+1)
    for subsuite in suite.suites:
        process_suite(subsuite, writer, items, level+1)
    for test in suite.tests:
        process_test(test, writer, items, level+1)

def process_test(test, writer, items, level):
    if 'test' in items:
        process_item(test, writer, level, 'Test')
    if 'keyword' in items:
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
    if not (2 <= len(sys.argv) <= 4) or '--help' in sys.argv:
        print __doc__
        sys.exit(1)
    inxml = sys.argv[1]
    if len(sys.argv) == 2:
        outcsv = os.path.splitext(inxml)[0] + '.csv'
    else:
        outcsv = sys.argv[2]
    if len(sys.argv) == 4:
        items = sys.argv[3]            
    else:
        items = 'suite-test-keyword'
    process_file(inxml, outcsv, items)
    print os.path.abspath(outcsv)
