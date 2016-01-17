#!/usr/bin/python

from robot.api import SuiteVisitor
import re


class Setup(SuiteVisitor):
    """Visitor that disables setup for suite or test case"""

    def __init__(self, phase='all'):
        self.phase = phase
        

    def start_suite(self, suite):
        """Remove setup for test suite"""
        if self.phase in ['suite','all']:
            test.keywords.setup.name = None

    def visit_test(self, test):      
        """Remove setup for test case"""
        if self.phase in ['test','all']:
            test.keywords.setup.name = None


class Teardown(SuiteVisitor):
    """Visitor that disables teardown for suite or test case"""

    def __init__(self, phase='all'):
        self.phase = phase
        

    def start_suite(self, suite):
        """Remove teardown for test suite"""
        if self.phase in ['suite','all']:
            test.keywords.teardown.name = None

    def visit_test(self, test):  
        """Remove teardown for test cases"""
        if self.phase in ['test','all']:
            test.keywords.teardown.name = None
