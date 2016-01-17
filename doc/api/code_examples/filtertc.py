#!/usr/bin/python

from robot.api import SuiteVisitor
import re


class Tests(SuiteVisitor):
    """Visitor that filters out test cases that would normally be executed"""

    def __init__(self, search):
        self.search = search
        

    def start_suite(self, suite):
        """Remove tests that match the string passed into constructor"""
        if len(suite.tests) < 1:
            return
        suite.tests = [t for t in suite.tests if self.search not in t.name]
       
        
    def end_suite(self, suite):
        """Remove suites that are empty after removing tests."""
        suite.suites = [s for s in suite.suites if s.test_count > 0]


    def visit_test(self, test):
        """Save time to avoid visiting tests and their keywords."""
        pass


class Suites(SuiteVisitor):
    """Visitor that filters out test cases that would normally be executed"""

    def __init__(self, search):
        self.search = search
        

    def start_suite(self, suite):
        """Remove tests whose parent or ancestor suites match the string passed into constructor"""
        if len(suite.tests) < 1:
            return
        test = suite.tests[0]
        suite_search = re.compile('(.*)(\.{0})'.format(test.name))
        suite_filter = suite_search.match(test.longname).group(1)
        suite.tests = [t for t in suite.tests if self.search not in suite_filter]
       
        
    def end_suite(self, suite):
        """Remove suites that are empty after removing tests."""
        suite.suites = [s for s in suite.suites if s.test_count > 0]


    def visit_test(self, test):
        """Save time to avoid visiting tests and their keywords."""
        pass
