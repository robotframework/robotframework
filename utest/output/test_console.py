import unittest
import sys

from robot.utils.asserts import assert_equal
from robot.output.console.verbose import VerboseOutput

# Overwrite IronPython's special utils.isatty with version using stream.isatty.
# Otherwise our StreamStub.isatty would not really work.
if sys.platform == 'cli':
    from robot.output.console import verbose
    verbose.isatty = lambda stream: hasattr(stream, 'isatty') and stream.isatty()


class TestBaseKeywordNotification(unittest.TestCase):

    def setUp(self, markers='AUTO', isatty=True):
        self.stream = StreamStub(isatty)
        self.console = VerboseOutput(width=16, colors='off', markers=markers,
                                     stdout=self.stream, stderr=self.stream)
        self.console.start_test(Stub())

    def test_markers_off(self):
        self.setUp(markers='OFF')
        self._write_marker()
        self._write_marker('FAIL')
        self._verify()

    def test_markers_auto_off(self):
        self.setUp(markers='AUTO', isatty=False)
        self._write_marker()
        self._write_marker('FAIL')
        self._verify()

    def _write_marker(self, status='PASS', count=1):
        for i in range(count):
            self.console.start_keyword(Stub(name=i))
            self.console.end_keyword(Stub(name=i, status=status))

    def _verify(self, after='', before=''):
        assert_equal(str(self.stream), '%sX :: D  %s' % (before, after))

    def _get_keyword(self, name, status):
        name_indented = '    ' + name
        pad_len = 16 - len(name_indented) - len(status)
        pad = ' ' * pad_len
        return '%s%s%s\n' % (name_indented, pad, status)

    def _verify_keyword(self, name='', status=''):
        assert_equal(str(self.stream), self._get_keyword(name, status))


class TestKeywordNotification(TestBaseKeywordNotification):

    def test_write_notrun_marker(self):
        self._write_marker(status='NOT-RUN')
        self._verify('.')

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

    def test_markers_on(self):
        self.setUp(markers='on', isatty=False)
        self._write_marker()
        self._write_marker('FAIL')
        self._verify('.F')


class TestDepthKeywordNotification(TestBaseKeywordNotification):

    def setUp(self, markers='AUTO', isatty=True):
        self.stream = StreamStub(isatty)
        self.console = VerboseOutput(width=16, colors='off', markers=markers,
                                     stdout=self.stream, stderr=self.stream)
        self.console.verbose_keywords()
        self.console.start_test(Stub())

    def test_write_pass_marker(self):
        self._write_marker()
        self._verify_keyword('0', '| PASS |')

    def test_write_fail_marker(self):
        self._write_marker('FAIL')
        self._verify_keyword('0', '| FAIL |')

    def test_multiple_markers(self):
        self.console.start_keyword(Stub(name='0'))
        self.console.start_keyword(Stub(name='1'))
        self._verify('\n    0   ')
        self.console.end_keyword(Stub(name='1', status='PASS'))
        self._verify('\n    0   .')
        self.console.end_keyword(Stub(name='0', status='PASS'))
        self._verify_keyword('0', '| PASS |')

    def test_markers_on(self):
        self.setUp(markers='on', isatty=False)
        self._write_marker()
        self._verify_keyword('0', '| PASS |')
        self._write_marker('FAIL')
        self._verify_keyword('0', '| FAIL |')


class Stub(object):

    def __init__(self, name='X', args=[], doc='D', status='PASS', message=''):
        self.name = name
        self.args = args
        self.doc = doc
        self.status = status
        self.message = message
        self.type = None

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
