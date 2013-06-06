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

"""Diff Tool for Robot Framework Outputs

Usage:  robotdiff.py [options] input_files

This script compares two or more Robot Framework output files and creates a
report where possible differences between test case statuses in each file
are highlighted. Main use case is verifying that results from executing same
test cases in different environments are same. For example, it is possible to
test that new Robot Framework version does not affect test results. Another
usage is comparing earlier test results with newer ones to find out possible
status changes and added test cases.

Options:
 -r --report file         HTML report file (created from the input files).
                          Default is 'robotdiff.html'.
 -n --name name *         Custom names for test runs. If this option is used,
                          it must be used as many times as there are input
                          files. By default test run names are got from the
                          input file names.
 -t --title title         Title for the generated diff report. The default
                          title is 'Test Run Diff Report'.
 -E --escape what:with *  Escape certain characters which are problematic in
                          console. 'what' is the name of the character to
                          escape and 'with' is the string to escape it with.
                          Available character to escape:
                          <--------------------ESCAPES------------------------>
                          Example:
                          --escape space:_ --title My_Fine_Diff_Report
 -h -? --help             Print this usage instruction.

Options that can be specified multiple times are marked with an asterisk (*).

Examples:
$ robotdiff.py output1.xml output2.xml output3.xml
$ robotdiff.py --name Env1 --name Env2 smoke1.xml smoke2.xml
"""

import sys
import os.path

from robot.utils import ArgumentParser, NormalizedDict, HtmlWriter
from robot.result import ExecutionResult
from robot.errors import DataError, Information


def main(args):
    opts, paths = _process_args(args)
    results = DiffResults()
    for path, name in zip(paths, _get_names(opts['name'], paths)):
        try:
            results.add_output(path, name)
        except DataError, err:
            _exit(err, error=True)
    reporter = DiffReporter(opts['report'], opts['title'])
    reporter.report(results)
    _exit('Report: %s' % reporter.outpath)

def _process_args(cliargs):
    ap = ArgumentParser(__doc__, arg_limits=(2, ))
    try:
        return ap.parse_args(cliargs)
    except Information, msg:
        _exit(msg)
    except DataError, err:
        _exit(err, error=True)

def _get_names(names, paths):
    if not names:
        return [None] * len(paths)
    if len(names) == len(paths):
        return names
    _exit('Different number of test run names (%d) and input files (%d).'
          % (len(names), len(paths)), error=True)

def _exit(msg, error=False):
    print unicode(msg)
    if error:
        print "\nTry --help for usage information."
    sys.exit(int(error))


class DiffResults(object):

    def __init__(self):
        self._stats = NormalizedDict()
        self.column_names = []

    @property
    def rows(self):
        return (RowStatus(name, statuses)
                for name, statuses in sorted(self._stats.items()))

    def add_output(self, path, column=None):
        self._add_suite(ExecutionResult(path).suite)
        self.column_names.append(column or path)
        for stats in self._stats.values():
            self._add_missing_statuses(stats)

    def _add_suite(self, suite):
        self._add_to_stats(suite)
        for sub_suite in suite.suites:
            self._add_suite(sub_suite)
        for test in suite.tests:
            self._add_to_stats(test)

    def _add_to_stats(self, item):
        stats = self._stats.setdefault(item.longname, [])
        self._add_missing_statuses(stats)
        stats.append(ItemStatus(item))

    def _add_missing_statuses(self, stats):
        while len(stats) < len(self.column_names):
            stats.append(MissingStatus())


class MissingStatus(object):
    name = 'N/A'
    status = 'not_available'


class ItemStatus(object):

    def __init__(self, item):
        self.name = item.status
        self.status = item.status.lower()


class RowStatus(object):

    def __init__(self, name, statuses):
        self.name = name
        self._statuses = statuses

    @property
    def status(self):
        passed = any(stat.name == 'PASS' for stat in self)
        failed = any(stat.name == 'FAIL' for stat in self)
        missing = any(stat.name == 'N/A' for stat in self)
        if passed and failed:
            return 'diff'
        if missing:
            return 'missing'
        return 'all_passed' if passed else 'all_failed'

    @property
    def explanation(self):
        return {'all_passed': 'All passed',
                'all_failed': 'All failed',
                'missing': 'Missing items',
                'diff': 'Different statuses'}[self.status]

    def __iter__(self):
        return iter(self._statuses)


class DiffReporter(object):

    def __init__(self, outpath=None, title=None):
        self.outpath = os.path.abspath(outpath or 'robotdiff.html')
        self._title = title or 'Test Run Diff Report'
        self._writer = HtmlWriter(open(self.outpath, 'w'))

    def report(self, results):
        self._start(results.column_names)
        for row in results.rows:
            self._write_row(row)
        self._end()

    def _start(self, columns):
        self._writer.content(START_HTML % {'TITLE': self._title}, escape=False)
        self._writer.start('tr')
        self._writer.element('th', 'Name', {'class': 'col_name'})
        for name in columns:
            self._writer.element('th', name, {'class': 'col_status'})
        self._writer.end('tr')

    def _write_row(self, row):
        self._writer.start('tr')
        self._write_name(row)
        for item in row:
            self._write_status(item)
        self._writer.end('tr')

    def _write_name(self, row):
        self._writer.element('td', row.name, {'class': 'col_name ' + row.status,
                                              'title': row.explanation})

    def _write_status(self, item):
        self._writer.element('td', item.name,
                             {'class': 'col_status ' + item.status})

    def _end(self):
        for tag in 'table', 'body', 'html':
            self._writer.end(tag)
        self._writer.close()


START_HTML = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="Expires" content="Mon, 20 Jan 2001 20:01:21 GMT">
<style media="all" type="text/css">
  body {
    background: white;
    font-family: sans-serif;
    font-size: 0.8em;
    color: black;
  }
  table {
    border: 1px solid black;
    border-collapse: collapse;
    empty-cells: show;
    margin: 0px 1px;
  }
  th, td {
    border: 1px solid black;
  }
  th {
    background: #C6C6C6;
  }
  .col_name {
    min-width: 25em;
    font-weight: bold;
  }
  .col_status {
    min-width: 6em;
    text-align: center;
  }
  .pass {
    color: #0F0;
  }
  .fail {
    color: #F00;
  }
  .not_available {
    color: #777;
  }
  .all_passed, .all_failed {
    background: #0F0;
  }
  .missing {
    background: #FF0;
  }
  .diff {
    background: #F00;
  }
</style>
<title>%(TITLE)s</title>
</head>
<body>
<h1>%(TITLE)s</h1>
<table>
'''[1:]


if __name__ == '__main__':
    main(sys.argv[1:])
