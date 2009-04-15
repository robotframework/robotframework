import unittest
import sys

from robot.output.listeners import Listeners
from robot.output import LOGGER
from robot.utils.asserts import *
from robot import utils


class _Mock:
    def __getattr__(self, name):
        return ''

class SuiteMock(_Mock):
    def __init__(self):
        self.name = 'suitemock'
        self.doc = 'somedoc'
        self.status = 'PASS'

    def get_stat_message(self):
        return 'full message'

    def get_full_message(self):
        return 'full message'

class TestMock(_Mock):
    def __init__(self):
        self.name = 'testmock'
        self.doc = 'cod'
        self.tags = ['foo', 'bar']
        self.message = 'Expected failure'
        self.status = 'FAIL'

class KwMock(_Mock):
    def __init__(self):
        self.name = 'kwmock'
        self.args = ['a1', 'a2']
        self.status = 'PASS'


class ListenAllOldStyle:
    
    def start_suite(self, name, doc):
        print "SUITE START: %s '%s'" % (name, doc)
    def start_test(self, name, doc, tags):
        tags = ', '.join([ str(tag) for tag in tags ])
        print "TEST START: %s '%s' %s" % (name, doc, tags)
    def start_keyword(self, name, args):
        args = [ str(arg) for arg in args ]
        print "KW START: %s %s" % (name, args)
    def end_keyword(self, status):
        print "KW END: %s" % (status)
    def end_test(self, status, message):
        if status == 'PASS':
            print 'TEST END: PASS'
        else:
            print "TEST END: %s %s" % (status, message)        
    def end_suite(self, status, message):
        print 'SUITE END: %s %s' % (status, message)
    def output_file(self, path):
        self._out_file('Output', path)
    def summary_file(self, path):
        self._out_file('Summary', path)
    def report_file(self, path):
        self._out_file('Report', path)
    def log_file(self, path):
        self._out_file('Log', path)
    def debug_file(self, path):
        self._out_file('Debug', path)
    def _out_file(self, name, path):
        print '%s: %s' % (name, path)
    def close(self):
        print 'Closing...'


class ListenAllNewStyle:

    ROBOT_LISTENER_API_VERSION = '2'
    
    def start_suite(self, name, attrs):
        print "SUITE START: %s '%s'" % (name, attrs['doc'])
    def start_test(self, name, attrs):
        print "TEST START: %s '%s' %s" % (name, attrs['doc'], 
                                          ', '.join(attrs['tags']))
    def start_keyword(self, name, attrs):
        args = [ str(arg) for arg in attrs['args'] ]
        print "KW START: %s %s" % (name, args)
    def end_keyword(self, name, attrs):
        print "KW END: %s" % attrs['status']
    def end_test(self, name, attrs):
        if attrs['status'] == 'PASS':
            print 'TEST END: PASS'
        else:
            print "TEST END: %s %s" % (attrs['status'], attrs['message'])        
    def end_suite(self, name, attrs):
        print 'SUITE END: %s %s' % (attrs['status'], attrs['statistics'])
    def output_file(self, path):
        self._out_file('Output', path)
    def summary_file(self, path):
        self._out_file('Summary', path)
    def report_file(self, path):
        self._out_file('Report', path)
    def log_file(self, path):
        self._out_file('Log', path)
    def debug_file(self, path):
        self._out_file('Debug', path)
    def _out_file(self, name, path):
        print '%s: %s' % (name, path)
    def close(self):
        print 'Closing...'


class InvalidListenerOldStyle:

    def start_suite(self, wrong, number, of, args):
        pass

    end_suite = start_test = end_test = start_keyword = end_keyword =\
    log_file = close = lambda self, *args: 1/0


class _BaseListenerTest:

    def setUp(self):
        self.listeners = Listeners([(self.listener_name, [])])
        self.listener = self.listeners._listeners[0]
        utils.capture_output()

    def test_start_suite(self):
        self.listeners.start_suite(SuiteMock())
        self._assert_output("SUITE START: suitemock 'somedoc'")

    def test_start_test(self):
        self.listeners.start_test(TestMock())
        self._assert_output("TEST START: testmock 'cod' foo, bar")

    def test_start_keyword(self):
        self.listeners.start_keyword(KwMock())
        self._assert_output("KW START: kwmock ['a1', 'a2']")

    def test_end_keyword(self):
        self.listeners.end_keyword(KwMock())
        self._assert_output("KW END: PASS")

    def test_end_test(self):
        self.listeners.end_test(TestMock())
        self._assert_output('TEST END: FAIL Expected failure')

    def test_end_suite(self):
        self.listeners.end_suite(SuiteMock())
        self._assert_output('SUITE END: PASS full message')

    def test_output_file(self):
        self.listeners.output_file('output', 'path/to/output')
        self._assert_output('Output: path/to/output')

    def test_log_file(self):
        self.listeners.output_file('log', 'path/to/log')
        self._assert_output('Log: path/to/log')

    def test_report_file(self):
        self.listeners.output_file('report', 'path/to/report')
        self._assert_output('Report: path/to/report')

    def test_summary_file(self):
        self.listeners.output_file('summary', 'path/to/summary')
        self._assert_output('Summary: path/to/summary')

    def test_debug_file(self):
        self.listeners.output_file('debug', 'path/to/debug')
        self._assert_output('Debug: path/to/debug')

    def test_close(self):
        self.listeners.close()
        self._assert_output('Closing...')

    def _assert_output(self, expected):
        stdout, stderr = utils.release_output()
        assert_equals(stderr, '')
        assert_equals(stdout.rstrip(), expected)


class TestOldStyleListeners(_BaseListenerTest, unittest.TestCase):
    listener_name = 'test_listeners.ListenAllOldStyle'

    def test_importing(self):
        assert_equals(self.listener.version, 1)
        assert_false(self.listener.is_java)


class TestNewStyleListeners(_BaseListenerTest, unittest.TestCase):
    listener_name = 'test_listeners.ListenAllNewStyle'

    def test_importing(self):
        assert_equals(self.listener.version, 2)
        assert_false(self.listener.is_java)


class TestInvalidOldStyleListener(unittest.TestCase):

    def setUp(self):
        self._console_logger = LOGGER._loggers.pop(0)

    def tearDown(self):
        LOGGER._loggers.insert(0, self._console_logger)

    def test_calling_listener_methods_fails(self):
        listenres = Listeners([('test_listeners.InvalidListenerOldStyle', [])])
        for name, args in [('start_suite', [SuiteMock()]),
                          ('end_suite', [SuiteMock()]),
                          ('start_test', [TestMock()]),
                          ('end_test', [TestMock()]),
                          ('start_keyword', [KwMock()]),
                          ('end_keyword', [KwMock()]),
                          ('output_file', ['log', '/path']),
                          ('close', [])]:
            getattr(listenres, name)(*args)


if utils.is_jython:

    class TestJavaListener(_BaseListenerTest, unittest.TestCase):

        listener_name = 'NewStyleJavaListener'

        def test_importing(self):
            assert_equals(self.listener.version, 2)
            assert_true(self.listener.is_java)


if __name__ == '__main__':
    unittest.main()

