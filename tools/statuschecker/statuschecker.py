#!/usr/bin/env python

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


"""Robot Framework Test Status Checker

Usage:  statuschecker.py infile [outfile]

This tool processes Robot Framework output XML files and checks that test case
statuses and messages are as expected. Main use case is post-processing output
files got when testing Robot Framework test libraries using Robot Framework
itself. 

If output file is not given, the input file is considered to be also output 
file and it is edited in place.

By default all test cases are expected to 'PASS' and have no message. Changing
the expected status to 'FAIL' is done by having word 'FAIL' (in uppercase)
somewhere in the test case documentation. Expected error message must then be
given after 'FAIL'. Error message can also be specified as a regular
expression by prefixing it with string 'REGEXP:'. 

This tool also allows testing the created log messages. They are specified
using a syntax 'LOG x.y:z LEVEL Actual message', which is described in the
tool documentation.
"""

import re

from robot.output import TestSuite
            
            
def process_output(inpath, outpath=None):
    suite = TestSuite(inpath)
    _process_suite(suite)
    suite.write_to_file(outpath)
    return suite.critical_stats.failed

def _process_suite(suite):
    for subsuite in suite.suites:
        _process_suite(subsuite)
    for test in suite.tests:
        _process_test(test)
    
def _process_test(test):
    exp = _Expected(test.doc)
    _check_status(test, exp)
    if test.status == 'PASS':
        _check_logs(test, exp)
    
def _check_status(test, exp):
    if exp.status != test.status:
        test.status = 'FAIL'
        if exp.status == 'PASS':
            test.message = ("Test was expected to PASS but it FAILED. " 
                            "Error message:\n") + test.message
        else:
            test.message = ("Test was expected to FAIL but it PASSED. "
                            "Expected message:\n") + exp.message
    elif not _message_matches(test.message, exp.message):
        test.status = 'FAIL'
        test.message = ("Wrong error message.\n\nExpected:\n%s\n\nActual:\n%s\n"
                        % (exp.message, test.message))
    elif test.status == 'FAIL':
        test.status = 'PASS'
        test.message = 'Original test failed as expected.'
        
def  _message_matches(actual, expected):
    if actual == expected:
        return True
    if expected.startswith('REGEXP:'):
        pattern = '^%s$' % expected.replace('REGEXP:', '', 1).strip()
        if re.match(pattern, actual, re.DOTALL):
            return True
    return False

def _check_logs(test, exp):
    for kw_indices, msg_index, level, message in exp.logs:
        try:
            kw = test.keywords[kw_indices[0]]
            for index in kw_indices[1:]:
                kw = kw.keywords[index]
        except IndexError:
            indices = '.'.join([ str(i+1) for i in kw_indices ])
            test.status = 'FAIL'
            test.message = ("Test '%s' does not have keyword with index '%s'"
                            % (test.name, indices))
            return

        if len(kw.messages) <= msg_index:
            if message != 'NONE':
                test.status = 'FAIL'
                test.message = ("Keyword '%s' should have had at least %d "
                                "messages" % (kw.name, msg_index+1))
        else:
            if _check_log_level(level, test, kw, msg_index):
                _check_log_message(message, test, kw, msg_index)

def _check_log_level(expected, test, kw, index):
    actual = kw.messages[index].level
    if actual == expected:
        return True
    test.status = 'FAIL'
    test.message = ("Wrong level for message %d of keyword '%s'.\n\n"
                    "Expected: %s\nActual: %s.\n%s" 
                    % (index+1, kw.name, expected, actual, kw.messages[index].message))
    return False

def _check_log_message(expected, test, kw, index):
    actual = kw.messages[index].message.strip()
    if _message_matches(actual, expected):
        return True
    test.status = 'FAIL'
    test.message = ("Wrong content for message %d of keyword '%s'.\n\n"
                    "Expected:\n%s\n\nActual:\n%s" 
                    % (index+1, kw.name, expected, actual))
    return False


class _Expected:
    
    def __init__(self, doc):
        self.status, self.message = self._get_status_and_message(doc)
        self.logs = self._get_logs(doc)
        
    def _get_status_and_message(self, doc):
        if 'FAIL' in doc:
            return 'FAIL', doc.split('FAIL', 1)[1].split('LOG', 1)[0].strip()
        return 'PASS', ''
    
    def _get_logs(self, doc):
        logs = []
        for item in doc.split('LOG')[1:]:
            index_str, msg_str = item.strip().split(' ', 1)
            kw_indices, msg_index = self._get_indices(index_str)
            level, message = self._get_log_message(msg_str)
            logs.append((kw_indices, msg_index, level, message))            
        return logs
            
    def _get_indices(self, index_str):
        try:
            kw_indices, msg_index = index_str.split(':')
        except ValueError:
            kw_indices, msg_index = index_str, '1'
        kw_indices = [ int(index) - 1 for index in kw_indices.split('.') ]
        return kw_indices, int(msg_index) - 1
            
    def _get_log_message(self, msg_str):
        try:
            level, message = msg_str.split(' ', 1)
            if level not in ['TRACE', 'DEBUG', 'INFO', 'WARN', 'FAIL']:
                raise ValueError
        except ValueError:
            level, message = 'INFO', msg_str
        return level, message

        
if __name__=='__main__':
    import sys
    import os

    if not 2 <= len(sys.argv) <= 3 or '--help' in sys.argv:
        print __doc__ 
        sys.exit(1)
    infile = sys.argv[1]
    outfile = len(sys.argv) == 3 and sys.argv[2] or None
    print  "Checking %s" % os.path.abspath(infile)
    rc = process_output(infile, outfile)
    if outfile:
        print "Output %s" % os.path.abspath(outfile)
    if rc > 255:
        rc = 255
    sys.exit(rc)
