import unittest
import time

from robot.output.filelogger import FileLogger
from robot.utils import StringIO, robottime
from robot.utils.asserts import *
from robot.utils.robottime import TimestampCache


class _FakeTimeCache(TimestampCache):

    def __init__(self):
        TimestampCache.__init__(self)

    def _get_epoch(self):
        return 1613230353.123 + time.timezone


class TestFileLogger(unittest.TestCase):

    def setUp(self):
        robottime.TIMESTAMP_CACHE = _FakeTimeCache()
        FileLogger._get_writer = lambda *args: StringIO()
        self.logger = FileLogger('whatever', 'INFO')

    def tearDown(self):
        robottime.TIMESTAMP_CACHE = TimestampCache()

    def test_write(self):
        self.logger.write('my message', 'INFO')
        expected = '20210213 15:32:33.123 | INFO  | my message\n'
        self._verify_message(expected)
        self.logger.write('my 2nd msg\nwith 2 lines', 'ERROR')
        expected += '20210213 15:32:33.123 | ERROR | my 2nd msg\nwith 2 lines\n'
        self._verify_message(expected)

    def test_write_helpers(self):
        self.logger.info('my message')
        expected = '20210213 15:32:33.123 | INFO  | my message\n'
        self._verify_message(expected)
        self.logger.warn('my 2nd msg\nwith 2 lines')
        expected += '20210213 15:32:33.123 | WARN  | my 2nd msg\nwith 2 lines\n'
        self._verify_message(expected)

    def test_set_level(self):
        self.logger.write('msg', 'DEBUG')
        self._verify_message('')
        self.logger.set_level('DEBUG')
        self.logger.write('msg', 'DEBUG')
        self._verify_message('20210213 15:32:33.123 | DEBUG | msg\n')

    def _verify_message(self, expected):
        assert_equal(self.logger._writer.getvalue(), expected)


if __name__ == "__main__":
    unittest.main()
