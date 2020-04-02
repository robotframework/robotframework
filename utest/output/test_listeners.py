from __future__ import print_function

import unittest

from robot.output.listeners import Listeners, LibraryListeners
from robot.output import LOGGER
from robot.running.outputcapture import OutputCapturer
from robot.utils.asserts import assert_equal, assert_raises
from robot.utils import DotDict, JYTHON


LOGGER.unregister_console_logger()


class Mock(object):

    def __getattr__(self, name):
        return ''


class SuiteMock(Mock):

    def __init__(self):
        self.name = 'suitemock'
        self.doc = 'somedoc'
        self.status = 'PASS'
        self.tests = self.suites = []

    stat_message = 'stat message'
    full_message = 'full message'


class TestMock(Mock):

    def __init__(self):
        self.name = 'testmock'
        self.doc = 'cod'
        self.tags = ['foo', 'bar']
        self.message = 'Expected failure'
        self.status = 'FAIL'
        self.data = DotDict({'name':self.name})


class KwMock(Mock):

    def __init__(self):
        self.name = 'kwmock'
        self.args = ['a1', 'a2']
        self.status = 'PASS'
        self.type = 'kw'


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


class ListenAll(ListenOutputs):
    ROBOT_LISTENER_API_VERSION = '2'

    def start_suite(self, name, attrs):
        print("SUITE START: %s '%s'" % (name, attrs['doc']))

    def start_test(self, name, attrs):
        print("TEST START: %s '%s' %s" % (name, attrs['doc'],
                                          ', '.join(attrs['tags'])))

    def start_keyword(self, name, attrs):
        args = [str(arg) for arg in attrs['args']]
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


class TestListeners(unittest.TestCase):
    listener_name = 'test_listeners.ListenAll'
    stat_message = 'stat message'

    def setUp(self):
        self.listeners = Listeners([self.listener_name])
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
        assert_equal(stderr, '')
        assert_equal(stdout.rstrip(), expected)


if JYTHON:

    class TestJavaListeners(TestListeners):
        listener_name = 'NewStyleJavaListener'
        stat_message = 'stat message'


class TestAttributesAreNotAccessedUnnecessarily(unittest.TestCase):

    def test_start_and_end_methods(self):
        for listeners in [Listeners([]), LibraryListeners()]:
            for name in dir(listeners):
                if name.startswith(('start_', 'end_')):
                    method = getattr(listeners, name)
                    method(None)

    def test_message_methods(self):
        class Message(object):
            level = 'INFO'
        for listeners in [Listeners([]), LibraryListeners()]:
            listeners.log_message(Message)
            listeners.message(Message)

    def test_some_methods_implemented(self):
        class MyListener(object):
            ROBOT_LISTENER_API_VERSION = 2
            def end_suite(self, suite):
                pass
        libs = LibraryListeners()
        libs.new_suite_scope()
        libs.register([MyListener()], None)
        for listeners in [Listeners([MyListener()]), libs]:
            listeners.start_suite(None)
            assert_raises(AttributeError, listeners.end_suite, None)


if __name__ == '__main__':
    unittest.main()
