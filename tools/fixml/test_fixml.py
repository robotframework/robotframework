#!/usr/bin/env python

import os
import sys
import subprocess
import unittest

BASEDIR = os.path.dirname(os.path.abspath(__file__))
# Ensure robot found in PYTHONPATH
sys.path.insert(0, os.path.join(BASEDIR, '..', '..', 'src'))

from robot.output import TestSuite
from robot.utils.asserts import assert_equals, assert_true

OUTDIR = os.path.join(BASEDIR, 'test', 'output')
if not os.path.exists(OUTDIR):
    os.mkdir(OUTDIR)


class TestFixml(unittest.TestCase):

    def test_missing_kw_in_passing_test(self):
        suite = self._fix_xml_and_parse('passing_kw_missing_end_tag')
        assert_equals(len(suite.tests), 2)
        self._assert_statistics(suite, 1, 1)
        assert_equals(len(suite.tests[0].keywords[0].keywords), 2)

    def test_missing_kw_in_failing_test(self):
        suite = self._fix_xml_and_parse('failing_kw_missing_end_tag')
        assert_equals(len(suite.tests), 2)
        self._assert_statistics(suite, 1, 1)
        assert_equals(len(suite.tests[1].keywords[0].keywords), 1)

    def test_xml_cut_inside_keyword(self):
        suite = self._fix_xml_and_parse('cut_inside_kw')
        assert_equals(len(suite.tests), 1)
        self._assert_statistics(suite, 0, 1)
        assert_equals(len(suite.tests[0].keywords[0].keywords), 2)

    def test_xml_cut_inside_msg_tag(self):
        suite = self._fix_xml_and_parse('cut_inside_msg')
        assert_equals(len(suite.tests), 2)
        self._assert_statistics(suite, 1, 1)
        assert_equals(len(suite.tests[1].keywords[0].keywords), 1)

    def _fix_xml_and_parse(self, base):
        outfile = self._fix_xml(base)
        return TestSuite(outfile).suites[0]

    def _fix_xml(self, base):
        infile = os.path.join('test', '%s.xml' % base)
        outfile = os.path.join(OUTDIR, '%s-fixed.xml' % base)
        subprocess.call(['python', 'fixml.py', infile, outfile])
        return outfile

    def _assert_statistics(self, suite, passed, failed):
        assert_equals(suite.critical_stats.passed, passed)
        assert_equals(suite.critical_stats.failed, failed)


if __name__ == '__main__':
    unittest.main()
