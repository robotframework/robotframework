#!/usr/bin/env python

#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
 -n --name name *         Name for test run. Different test runs can be named
                          with this option. However, there must be as many
                          names as there are input files. By default the name
                          of the input files are used as names. Input files
                          having same file name are distinguished by adding
                          as many parent directories to the names as is needed.
 -t --title title         Title for the generated diff report. The default
                          title is 'Diff Report'.
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

import os
import sys

from robot import utils
from robot.output import TestSuite
from robot.errors import DataError, Information


def main(args):
    opts, paths = _process_args(args)
    diff = DiffRobotOutputs(opts['report'], opts['title'])
    names = _get_names(opts['name'], paths)
    for path, name in zip(paths, names):
        try:
            diff.add_suite(path, name)
        except DataError, err:
            exit(error=str(err))
    diff.serialize()
    print "Report: %s" % diff.close()

def _process_args(cliargs):
    ap = utils.ArgumentParser(__doc__, arg_limits=(2, sys.maxint))
    try:
        opts, paths = ap.parse_args(cliargs, unescape='escape', help='help',
                                    check_args=True)
    except Information, msg:
        exit(msg=str(msg))
    except DataError, err:
        exit(error=str(err))
    return opts, [ utils.normpath(path) for path in paths ]

def _get_names(names, paths):
    if not names:
        return [None] * len(paths)
    if len(names) == len(paths):
        return names
    exit(error="Different number of names (%d) and inputs (%d)"
         % (len(names), len(paths)))


def exit(rc=0, error=None, msg=None):
    if error:
        print error, "\n\nUse '--help' option to get usage information."
        if rc == 0:
            rc = 255
    if msg:
        print msg
        rc = 1
    sys.exit(rc)


class DiffRobotOutputs:

    def __init__(self, outpath=None, title=None):
        if not outpath:
            outpath = 'robotdiff.html'
        if not title:
            title = 'Diff Report'
        self._output = open(utils.normpath(outpath), 'w')
        self._writer = utils.HtmlWriter(self._output)
        self.title = title
        self.column_names = []
        self.suites_and_tests = {}

    def add_suite(self, path, column_name=None):
        if not column_name:
            column_name = path
        column_name = self._get_new_column_name(column_name)
        self.column_names.append(column_name)
        suite = TestSuite(path)
        # Creates links to logs
        link = self._get_loglink(path, self._output.name)
        self._set_suite_links(suite, link)
        self._add_suite(suite, column_name)

    def _get_loglink(self, inpath, target):
        """Finds matching log file and return link to it or None."""
        indir, infile = os.path.split(inpath)
        logname = os.path.splitext(infile.lower())[0]
        if logname.endswith('output'):
            logname = logname[:-6] + 'log'
        for item in os.listdir(indir):
            name, ext = os.path.splitext(item.lower())
            if name == logname and ext in ['.html','.htm','.xhtml']:
                logpath = os.path.join(indir, item)
                return utils.get_link_path(logpath, target)
        return None

    def _set_suite_links(self, suite, link):
        suite.link = link
        for sub_suite in suite.suites:
            self._set_suite_links(sub_suite, link)
        for test in suite.tests:
            test.link = link

    def _get_new_column_name(self, column_name):
        if column_name not in self.column_names:
            return column_name
        count = 0
        for name in self.column_names:
            if name.startswith(column_name):
                count += 1
        return column_name + '_%d' % (count)

    def _add_suite(self, suite, column_name):
        self._add_to_dict(suite, column_name)
        for sub_suite in suite.suites:
            self._add_suite(sub_suite, column_name)
        for test in suite.tests:
            self._add_to_dict(test, column_name)

    def _add_to_dict(self, s_or_t, column_name):
        name = s_or_t.longname.replace('_', ' ')
        keys = self.suites_and_tests.keys()
        found = False
        for key in keys:
            if utils.normalize(name, caseless=True, spaceless=True) == \
                utils.normalize(key, caseless=True, spaceless=True):
                found = True
                foundkey = key
        if not found:
            self.suites_and_tests[name] =  [(column_name, s_or_t)]
        else:
            self.suites_and_tests[foundkey].append((column_name, s_or_t))

    def serialize(self):
        self._write_start()
        self._write_headers()
        for name, value in sorted(self.suites_and_tests.items()):
            self._write_start_of_s_or_t_row(name, value)
            for column_name in self.column_names:
                #Generates column containg status
                s_or_t = self._get_s_or_t_by_column_name(column_name, value)
                self._write_status(s_or_t)
            self._writer.end('tr', newline=True)
        self._writer.end('table', newline=True)
        self._write_end()

    def close(self):
        self._output.close()
        return self._output.name

    def _write_status(self, item):
        if item:
            self._col_status_content(item)
        else:
            attrs = {'class': 'col_status not_available'}
            self._writer.element('td', 'N/A', attrs)

    def _col_status_content(self, s_or_t):
        status = s_or_t.status
        col_status = 'col_status %s' % status.lower()
        self._writer.start('td', {'class': col_status})
        if s_or_t.link is not None:
            type = self._get_type(s_or_t)
            link = '%s#%s_%s' % (s_or_t.link, type, s_or_t.longname)
            self._writer.element('a', status, {'class': status.lower(),
                                               'href': link,
                                               'title': s_or_t.longname})
        else:
            self._writer.content(status)
        self._writer.end('td')

    def _get_type(self, s_or_t):
        return 'suite' if hasattr(s_or_t, 'tests') else 'test'

    def _write_start_of_s_or_t_row(self, name, value):
        attrs = {'class': '%s col_name' % self._get_row_status(value)}
        self._writer.element('td', name, attrs)

    def _get_row_status(self, items):
        if not items:
            return 'none'
        status = self._get_status(items[0])
        for item in items:
            if self._get_status(item) != status:
                return 'diff'
        return 'all_%s' % status.lower()

    def _get_status(self, item):
        return item[1].status

    def _get_s_or_t_by_column_name(self, column_name, items):
        for item in items:
            if column_name == item[0]:
                return item[1]
        return None

    def _write_headers(self):
        self._writer.start('table')
        self._writer.start('tr')
        self._writer.element('th', 'Name', {'class': 'col_name'})
        for name in self.column_names:
            name = name.replace(self._get_prefix(self.column_names), '')
            self._writer.element('th', name, {'class': 'col_status'})
        self._writer.end('tr')

    def _get_prefix(self, paths):
        paths = [os.path.dirname(p) for p in paths]
        dirs = []
        for path in paths:
            if path.endswith(os.sep):
                dirs.append(path)
            else:
                if path != '' and path[-1] != os.sep:
                    dirs.append(path + os.sep)
                else:
                    dirs.append(path)
        prefix = os.path.commonprefix(dirs)
        while len(prefix) > 0:
            if prefix.endswith(os.sep):
                break
            prefix = prefix[:-1]
        return prefix

    def _write_start(self):
        self._output.write(START_HTML)
        self._output.write("<title>%s</title>\n</head>\n" % self.title)
        self._output.write("<body>\n<h1>%s</h1>\n" % self.title)

    def _write_end(self):
        self._writer.end('body')
        self._writer.end('html')


START_HTML = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="Expires" content="Mon, 20 Jan 2001 20:01:21 GMT" />
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
  .diff {
    background: red;
  }
  .all_pass {
    background: #00f000;
  }
  .all_fail {
    background: yellow;
  }
  .col_name {
    min-width: 20em;
    font-weight: bold;
  }
  .col_status {
    min-width: 6em;
    text-align: center;
  }
  .pass {
    color: #00f000;
  }
  .fail {
    color: red;
  }
  .not_available {
    color: gray;
  }
  a:link, a:visited {
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
    color: purple;
  }
</style>
<style media="print" type="text/css">
  body {
    font-size: 9pt;
  }
  a:link, a:visited {
    color: black;
  }
</style>
'''[1:]


if __name__ == '__main__':
    main(sys.argv[1:])
