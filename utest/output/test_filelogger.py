import unittest
from io import StringIO

from robot.output.filelogger import FileLogger
from robot.utils.asserts import assert_equal


class LoggerSub(FileLogger):

    def _get_writer(self, path):
        return StringIO()

    def message(self, msg):
        msg.timestamp = '2023-09-08 12:16:00.123456'
        super().message(msg)


class TestFileLogger(unittest.TestCase):

    def setUp(self):
        self.logger = LoggerSub('whatever', 'INFO')

    def test_write(self):
        self.logger.write('my message', 'INFO')
        expected = '2023-09-08 12:16:00.123456 | INFO  | my message\n'
        self._verify_message(expected)
        self.logger.write('my 2nd msg\nwith 2 lines', 'ERROR')
        expected += '2023-09-08 12:16:00.123456 | ERROR | my 2nd msg\nwith 2 lines\n'
        self._verify_message(expected)

    def test_write_helpers(self):
        self.logger.info('my message')
        expected = '2023-09-08 12:16:00.123456 | INFO  | my message\n'
        self._verify_message(expected)
        self.logger.warn('my 2nd msg\nwith 2 lines')
        expected += '2023-09-08 12:16:00.123456 | WARN  | my 2nd msg\nwith 2 lines\n'
        self._verify_message(expected)

    def test_set_level(self):
        self.logger.write('msg', 'DEBUG')
        self._verify_message('')
        self.logger.set_level('DEBUG')
        self.logger.write('msg', 'DEBUG')
        self._verify_message('2023-09-08 12:16:00.123456 | DEBUG | msg\n')

    def _verify_message(self, expected):
        assert_equal(self.logger._writer.getvalue(), expected)


if __name__ == "__main__":
    unittest.main()
