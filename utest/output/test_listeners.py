from __future__ import print_function
import unittest

from robot.output.listeners import Listeners
from robot.output import LOGGER
from robot.utils.asserts import *
from robot.utils import JYTHON
from robot.running.outputcapture import OutputCapturer


LOGGER.unregister_console_logger()


class _Mock:
    def __getattr__(self, name):
        return ''

class SuiteMock(_Mock):
    def __init__(self):
        self.name = 'suitemock'
        self.doc = 'somedoc'
        self.status = 'PASS'
        self.tests = self.suites = []

    stat_message = 'stat message'
    full_message = 'full message'

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


class ListenOutputs(object):

    def output_file(self, path):
        self._out_file('Output', path)

    def report_file(self, path):
        self._out_file('Report', path)

    def log_file(self, path):
        self._out_file('Log', path)

    def debug_file(self, path):
        self._out_file('Debug', path)

    def xunit_file(self, path):
        self._out_file('XUnit', path)

    def _out_file(self, name, path):
        print('%s: %s' % (name, path))


class ListenAllOldStyle(ListenOutputs):

    def start_suite(self, name, doc):
        print("SUITE START: %s '%s'" % (name, doc))
    def start_test(self, name, doc, tags):
        tags = ', '.join([ str(tag) for tag in tags ])
        print("TEST START: %s '%s' %s" % (name, doc, tags))
    def start_keyword(self, name, args):
        args = [ str(arg) for arg in args ]
        print("KW START: %s %s" % (name, args))
    def end_keyword(self, status):
        print("KW END: %s" % (status))
    def end_test(self, status, message):
        if status == 'PASS':
            print('TEST END: PASS')
        else:
            print("TEST END: %s %s" % (status, message))
    def end_suite(self, status, message):
        print('SUITE END: %s %s' % (status, message))

    def close(self):
        print('Closing...')


class ListenAllNewStyle(ListenOutputs):

    ROBOT_LISTENER_API_VERSION = '2'

    def start_suite(self, name, attrs):
        print("SUITE START: %s '%s'" % (name, attrs['doc']))
    def start_test(self, name, attrs):
        print("TEST START: %s '%s' %s" % (name, attrs['doc'],
                                          ', '.join(attrs['tags'])))
    def start_keyword(self, name, attrs):
        args = [ str(arg) for arg in attrs['args'] ]
        print("KW START: %s %s" % (name, args))
    def end_keyword(self, name, attrs):
        print("KW END: %s" % attrs['status'])
    def end_test(self, name, attrs):
        if attrs['status'] == 'PASS':
            print('TEST END: PASS')
        else:
            print("TEST END: %s %s" % (attrs['status'], attrs['message']))
    def end_suite(self, name, attrs):
        print('SUITE END: %s %s' % (attrs['status'], attrs['statistics']))
    def close(self):
        print('Closing...')


class InvalidListenerOldStyle:

    def start_suite(self, wrong, number, of, args):
        pass

    end_suite = start_test = end_test = start_keyword = end_keyword =\
    log_file = close = lambda self, *args: 1/0


class _BaseListenerTest:
    stat_message = ''

    def setUp(self):
        self.listeners = Listeners([self.listener_name])
        self.listener = self.listeners._listeners[0]
        self.capturer = OutputCapturer()

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
        self._assert_output('SUITE END: PASS ' + self.stat_message)

    def test_output_file(self):
        self.listeners.output_file('output', 'path/to/output')
        self._assert_output('Output: path/to/output')

    def test_log_file(self):
        self.listeners.output_file('log', 'path/to/log')
        self._assert_output('Log: path/to/log')

    def test_report_file(self):
        self.listeners.output_file('report', 'path/to/report')
        self._assert_output('Report: path/to/report')

    def test_debug_file(self):
        self.listeners.output_file('debug', 'path/to/debug')
        self._assert_output('Debug: path/to/debug')

    def test_xunit_file(self):
        self.listeners.output_file('XUnit', 'path/to/xunit')
        self._assert_output('XUnit: path/to/xunit')

    def test_close(self):
        self.listeners.close()
        self._assert_output('Closing...')

    def _assert_output(self, expected):
        stdout, stderr = self.capturer._release()
        assert_equals(stderr, '')
        assert_equals(stdout.rstrip(), expected)


class TestOldStyleListeners(_BaseListenerTest, unittest.TestCase):
    listener_name = 'test_listeners.ListenAllOldStyle'
    stat_message = 'full message'

    def test_importing(self):
        assert_equals(self.listener.version, 1)


class TestNewStyleListeners(_BaseListenerTest, unittest.TestCase):
    listener_name = 'test_listeners.ListenAllNewStyle'
    stat_message = 'stat message'

    def test_importing(self):
        assert_equals(self.listener.version, 2)


class TestInvalidOldStyleListener(unittest.TestCase):

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


if JYTHON:

    class TestJavaListener(_BaseListenerTest, unittest.TestCase):
        listener_name = 'NewStyleJavaListener'
        stat_message = 'stat message'

        def test_importing(self):
            assert_equals(self.listener.version, 2)


if __name__ == '__main__':
    unittest.main()
