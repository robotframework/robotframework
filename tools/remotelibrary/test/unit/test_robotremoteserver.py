#!/usr/bin/env python

import unittest
import sys
import os.path

remotedir = os.path.dirname(os.path.dirname(os.path.dirname((__file__))))
sys.path.insert(0, remotedir)

from robotremoteserver import RobotRemoteServer


class NonServingRemoteServer(RobotRemoteServer):
    def __init__(self, library):
        self._library = library

class StaticLibrary:
    def passing_keyword(self):
        pass
    def failing_keyword(self, exception, message='Hello, world!'):
        raise exception(message)
    def _not_included(self):
        """Starts with an underscore"""
    not_included = "Not a method or function"
    not_included_2 = NonServingRemoteServer  # Callable but not method/function

class HybridLibrary:
    def get_keyword_names(self):
        return [ n for n in dir(StaticLibrary) if n.endswith('_keyword') ] 
    def __getattr__(self, name):
        return getattr(StaticLibrary(), name)
    def not_included(self):
        """Not returned by get_keyword_names"""


class TestStaticApi(unittest.TestCase):
    library = StaticLibrary()

    def setUp(self):
        self.server = NonServingRemoteServer(self.library)

    def test_get_keyword_names(self):
        self.assertEquals(self.server.get_keyword_names(),
                          ['failing_keyword', 'passing_keyword',
                           'stop_remote_server'])

    def test_run_passing_keyword(self):
        self.assertEquals(self.server.run_keyword('passing_keyword', []),
                          {'status': 'PASS', 'output': '', 'traceback': '',
                           'return': '', 'error': ''})

    def test_run_failing_keyword(self):
        ret = self.server.run_keyword('failing_keyword', [ValueError])
        self.assertEquals(ret['status'], 'FAIL')
        self.assertEquals(ret['error'], 'ValueError: Hello, world!')

    def test_strip_generic_exception_names_from_error_messages(self):
        for exception in AssertionError, Exception, RuntimeError:
            ret = self.server.run_keyword('failing_keyword', [exception])
            self.assertEquals(ret['status'], 'FAIL')
            self.assertEquals(ret['error'], 'Hello, world!')

    def test_return_only_exception_name_if_no_error_message(self):
        for exception in AssertionError, ValueError:
            ret = self.server.run_keyword('failing_keyword', [exception, ''])
            self.assertEquals(ret['status'], 'FAIL')
            self.assertEquals(ret['error'], exception.__name__)
                

class TestHybridApi(TestStaticApi):
    library = HybridLibrary()

        
if __name__ == '__main__':
    unittest.main()
