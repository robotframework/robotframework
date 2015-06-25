import unittest
import sys

from robot.utils.asserts import assert_equals
from robot.output.console.verbose import VerboseOutput

# Overwrite IronPython's special utils.isatty with version using stream.isatty.
# Otherwise our StreamStub.isatty would not really work.
if sys.platform == 'cli':
    from robot.output.console import verbose
    verbose.isatty = lambda stream: hasattr(stream, 'isatty') and stream.isatty()


class TestKeywordNotification(unittest.TestCase):

    def setUp(self, markers='AUTO', isatty=True):
        self.stream = StreamStub(isatty)
        self.console = VerboseOutput(width=16, colors='off', markers=markers,
                                     stdout=self.stream, stderr=self.stream)
        self.console.start_test(Stub())

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
        self.console.end_test(Stub())
        self._verify('| PASS |\n%s\n' % ('-'*self.console._writer._width))

    def test_clear_markers_when_there_are_warnings(self):
        self._write_marker(count=5)
        self.console.message(MessageStub())
        self._verify(before='[ WARN ] Message\n')
        self._write_marker(count=2)
        self._verify(before='[ WARN ] Message\n', after='..')

    def test_markers_off(self):
        self.setUp(markers='OFF')
        self._write_marker()
        self._write_marker('FAIL')
        self._verify()

    def test_markers_on(self):
        self.setUp(markers='on', isatty=False)
        self._write_marker()
        self._write_marker('FAIL')
        self._verify('.F')

    def test_markers_auto_off(self):
        self.setUp(markers='AUTO', isatty=False)
        self._write_marker()
        self._write_marker('FAIL')
        self._verify()

    def _write_marker(self, status='PASS', count=1):
        for i in range(count):
            self.console.start_keyword(Stub())
            self.console.end_keyword(Stub(status=status))

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

    def __init__(self, isatty=True):
        self.buffer = []
        self.isatty = lambda: isatty

    def write(self, msg):
        self.buffer.append(msg)

    def flush(self):
        pass

    def __str__(self):
        return ''.join(self.buffer).rsplit('\r')[-1]


if __name__ == '__main__':
    unittest.main()
