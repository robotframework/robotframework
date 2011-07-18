#!/usr/bin/env python

import unittest
import StringIO
from os.path import join, abspath

from robot.utils.asserts import *

from risto import AllStatistics, Statistics, Plotter


AllStatistics._get_stats = lambda *args: []


class TestGetNamesFromPaths(unittest.TestCase):

    def _test(self, paths, expected):
        actual = AllStatistics([])._get_names(paths)
        assert_equals(actual, expected)

    def test_from_basename(self):
        self._test(['foo.xml','bar.xml'], ['Foo','Bar'])

    def test_from_basename_with_longer_path(self):
        paths = [join('my','path',str(i))+'.xml' for i in range(10)]
        self._test(paths, [str(i) for i in range(10)])

    def test_basename_used_if_only_one_path(self):
        self._test(['foo.xml'], ['Foo'])
        self._test([join('what','ever','foo.xml')], ['Foo'])

    def test_from_dirname(self):
        paths = [join('foo','out.xml'), join('bar','out.xml')]
        self._test(paths, ['Foo','Bar'])

    def test_from_dirname_with_longer_path(self):
        paths = [ abspath(join(str(i),'out.xml')) for i in range(10) ]
        self._test(paths, [ str(i) for i in range(10) ])

    def test_backslash_as_path_separator(self):
        self._test(['some\\path\\foo.xml'], ['Foo'])
        self._test(['c:\\temp\\f1.xml','c:\\temp\\f2.xml'], ['F 1','F 2'])

    def test_forwardslash_as_path_separator(self):
        self._test(['some/path/foo.xml'], ['Foo'])
        self._test(['/tmp/foo1.xml','/tmp/foo2.xml'], ['Foo 1','Foo 2'])

    def test_format_name(self):
        self._test(['with spaces.xml'], ['With Spaces'])
        self._test(['with_unders.xml'], ['With Unders'])
        self._test(['with_CAPS.xml'], ['With CAPS'])
        self._test(['camelCase.xml'], ['Camel Case'])
        self._test(['camelCase2.xml'], ['Camel Case 2'])
        self._test(['3rdCAMELCase.xml'], ['3 Rd CAMEL Case'])
        self._test(['p/n_1.xml','p/n_2.xml','p/n_3.xml'], ['N 1','N 2','N 3'])
        self._test(['  leading and trailing__.xml'], ['Leading And Trailing'])


class TestGetXTicks(unittest.TestCase):

    def _test(self, slen, limit, expected):
        actual = Plotter()._get_xticks(slen, limit)
        assert_equals(actual, expected)

    def test_one_stat(self):
        self._test(1, 10, [0])
        self._test(1, 42, [0])

    def test_less_than_limit(self):
        self._test(2, 10, [0,1])
        self._test(10, 20, range(10))

    def test_exactly_limit(self):
        self._test(10, 10, range(10))
        self._test(42, 42, range(42))

    def test_over_the_limit(self):
        for slen, exp in [(20,  [0,  3,  5,  7,  9, 11, 13, 15, 17,  19]),
                          (91,  [0, 10, 20, 30, 40, 50, 60, 70, 80,  90]),
                          (90,  [0, 10, 20, 30, 40, 50, 60, 70, 80,  89]),
                          (100, [0, 11, 22, 33, 44, 55, 66, 77, 88,  99]),
                          (101, [0, 12, 23, 34, 45, 56, 67, 78, 89, 100])]:
            self._test(slen, 10, exp)


class TestStatistics(unittest.TestCase):

    def setUp(self):
        self.stats = Statistics(StringIO.StringIO(OUTPUT), 'My Stats')

    def test_name(self):
        assert_equals(self.stats.name, 'My Stats')

    def test_totals(self):
        self._assert_tag_stat(self.stats.critical_tests, 3, 2)
        self._assert_tag_stat(self.stats.all_tests, 8, 2)

    def test_tags(self):
        data = [('t1', 4, 2,  True),
                ('sub3', 2, 0, False, True),
                ('d1 & d2', 1, 0, False, False, True),
                ('f1', 8, 2, False, False, False, 'forced')]
        for item in data:
            name, exp = item[0], item[1:]
            self._assert_tag_stat(self.stats[name], *exp)

    def _assert_tag_stat(self, stat, passed, failed, critical=False,
                         non_crit=False, combined=False, doc=''):
        assert_equals(stat.passed, passed, '%s passed' % stat.name)
        assert_equals(stat.failed, failed, '%s failed' % stat.name)
        assert_equals(stat.total, passed+failed, '%s total' % stat.name)
        assert_equals(stat.critical, critical, '%s critical' % stat.name)
        assert_equals(stat.non_critical, non_crit, '%s non-crit' % stat.name)
        assert_equals(stat.combined, combined, '%s combined' % stat.name)
        assert_equals(stat.doc, doc, '%s doc' % stat.name)


OUTPUT = """<?xml version="1.0" encoding="UTF-8"?>
<robot generated="20080325 12:29:43.180" generator="Robot 1.8.3">
<statistics>
<total>
<stat fail="2" pass="3">Critical Tests</stat>
<stat fail="2" pass="8">All Tests</stat>
</total>
<tag>
<stat fail="2" info="critical" pass="4">t1</stat>
<stat fail="0" info="non-critical" pass="2">sub3</stat>
<stat fail="0" info="combined" pass="1">d1 &amp; d2</stat>
<stat fail="0" info="" pass="1">d1</stat>
<stat fail="0" info="" pass="1">d2</stat>
<stat fail="2" info="" doc="forced" pass="8">f1</stat>
<stat fail="0" info="" pass="2">t2</stat>
</tag>
<suite>
<stat fail="2" doc="Suites" pass="8">Suites</stat>
<stat fail="1" doc="Suites.Fourth" pass="0">s.Fourth</stat>
<stat fail="1" doc="Suites.Subsuites" pass="1">s.Subsuites</stat>
<stat fail="1" doc="Suites.Subsuites.Sub 1" pass="0">s.s.Sub 1</stat>
<stat fail="0" doc="Suites.Subsuites.Sub 2" pass="1">s.s.Sub 2</stat>
<stat fail="0" doc="Suites.Subsuites 2" pass="2">s.Subsuites 2</stat>
<stat fail="0" doc="Suites.Subsuites 2.Subsuite 3" pass="2">s.s.Subsuite 3</stat>
<stat fail="0" doc="Suites.Tsuite 1" pass="3">s.Tsuite 1</stat>
<stat fail="0" doc="Suites.Tsuite 2" pass="1">s.Tsuite 2</stat>
<stat fail="0" doc="Suites.Tsuite 3" pass="1">s.Tsuite 3</stat>
</suite>
</statistics>
</robot>
"""


if __name__ == '__main__':
    unittest.main()
