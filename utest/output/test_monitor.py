import unittest
import re

from robot.utils.asserts import assert_equals
from robot.output.monitor import CommandLineMonitor


class TestKeywordNotification(unittest.TestCase):

    def setUp(self):
        self.stream = StreamStub()
        self.monitor = CommandLineMonitor(width=16, colors='off',
                                          stdout=self.stream, stderr=self.stream)
        self.monitor.start_test(Stub())

    def test_write_pass_marker(self):
        self._write_marker()
        self._verify('.')

    def test_write_fail_marker(self):
        self._write_marker('FAIL')
        self._verify('F')

    def test_multiple_markers(self):
        self._write_marker()
        self._write_marker('FAIL')
        self._write_marker('FAIL')
        self._write_marker()
        self._verify('.FF.')

    def test_maximum_number_of_markers(self):
        self._write_marker(count=8)
        self._verify('........')

    def test_more_markers_than_fit_into_status_area(self):
        self._write_marker(count=9)
        self._verify('.')
        self._write_marker(count=10)
        self._verify('...')

    def test_clear_markers_when_test_status_is_written(self):
        self._write_marker(count=5)
        self.monitor.end_test(Stub())
        self._verify('| PASS |\n%s\n' % ('-'*self.monitor._writer._width))

    def test_clear_markers_when_there_are_warnings(self):
        self._write_marker(count=5)
        self.monitor.message(MessageStub())
        self._verify(before='[ WARN ] Message\n')
        self._write_marker(count=2)
        self._verify(before='[ WARN ] Message\n', after='..')

    def _write_marker(self, status='PASS', count=1):
        for i in range(count):
            self.monitor.start_keyword(Stub())
            self.monitor.end_keyword(Stub(status=status))

    def _verify(self, after='', before=''):
        assert_equals(str(self.stream), '%sX :: D  %s' % (before, after))


class Stub(object):

    def __init__(self, name='X', doc='D', status='PASS', message=''):
        self.name = name
        self.doc = doc
        self.status = status
        self.message = message

    @property
    def passed(self):
        return self.status == 'PASS'


class MessageStub(object):

    def __init__(self, message='Message', level='WARN'):
        self.message = message
        self.level = level


class StreamStub(object):

    def __init__(self):
        self.buffer = []

    def write(self, msg):
        self.buffer.append(msg)

    def flush(self):
        pass

    def isatty(self):
        return True

    def __str__(self):
        return ''.join(self.buffer).rsplit('\r')[-1]


if __name__ == '__main__':
    unittest.main()
