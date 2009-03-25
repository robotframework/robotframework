import unittest
from StringIO import StringIO

from robot import utils
from robot.utils.asserts import *

from robot.output.systemlogger import _FileLogger, SystemLogger


class MessageMock:
    
    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message
    
class LoggerMock:

    def __init__(self, *expected):
        self.expected = list(expected)
    
    def write(self, msg, level):
        assert_equals(msg.level, level)
        exp_msg, exp_level = self.expected.pop(0)
        assert_equals(msg.level, exp_level)
        assert_equals(msg.message, exp_msg)
        self.msg = msg

    def copy(self):
        return LoggerMock(*self.expected)

class LoggerMock2(LoggerMock):

    def output_file(self, name, path):
        self.output_file = (name, path)

    def close(self):
        self.closed = True


class TestSystemFileLogger(unittest.TestCase):
    
    def setUp(self):
        _FileLogger._get_writer = lambda *args: StringIO()
        self.logger = _FileLogger('whatever', 'INFO')
        utils.robottime._current_time = (2006, 6, 13, 8, 37, 42, 123)
   
    def tearDown(self):
        utils.robottime._current_time = None

    def test_write(self):
        self.logger.write('my message', 'INFO')
        expected = '20060613 08:37:42.123 | INFO  | my message\n'
        assert_equals(self.logger._writer.getvalue(), expected)
        self.logger.write('my 2nd msg\nwith 2 lines', 'ERROR')
        expected += '20060613 08:37:42.123 | ERROR | my 2nd msg\nwith 2 lines\n'
        assert_equals(self.logger._writer.getvalue(), expected)
                        
    def test_write_helpers(self):
        self.logger.info('my message')
        expected = '20060613 08:37:42.123 | INFO  | my message\n'
        assert_equals(self.logger._writer.getvalue(), expected)
        self.logger.warn('my 2nd msg\nwith 2 lines')
        expected += '20060613 08:37:42.123 | WARN  | my 2nd msg\nwith 2 lines\n'
        assert_equals(self.logger._writer.getvalue(), expected)

    def test_set_level(self):
        self.logger.write('msg', 'DEBUG')
        assert_equals(self.logger._writer.getvalue(), '')
        self.logger.set_level('DEBUG')
        self.logger.write('msg', 'DEBUG')
        assert_equals(self.logger._writer.getvalue(), '20060613 08:37:42.123 | DEBUG | msg\n')
        

class TestSystemLogger(unittest.TestCase):
    
    def setUp(self):
        self.syslog = SystemLogger()

    def test_write_to_one_logger(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        self.syslog.register_logger(logger)
        self.syslog.write('Hello, world!')
        assert_true(logger.msg.timestamp.startswith('20'))

    def test_write_to_one_logger_with_trace_level(self):
        logger = LoggerMock(('expected message', 'TRACE'))
        self.syslog.register_logger(logger)
        self.syslog.write('expected message', 'TRACE')
        assert_true(hasattr(logger, 'msg'))
    
    def test_write_to_multiple_loggers(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        logger2 = logger.copy()
        logger3 = logger.copy()
        self.syslog.register_logger(logger, logger2, logger3)
        self.syslog.write('Hello, world!')
        assert_true(logger.msg is logger2.msg)
        assert_true(logger.msg is logger.msg)

    def test_write_multiple_messages(self):
        msgs = [('0', 'ERROR'), ('1', 'WARN'), ('2', 'INFO'), ('3', 'DEBUG'), ('4', 'TRACE')]
        logger = LoggerMock(*msgs)
        self.syslog.register_logger(logger)
        for msg, level in msgs:
            self.syslog.write(msg, level)
            assert_equals(logger.msg.message, msg)
            assert_equals(logger.msg.level, level)
        
    def test_all_methods(self):
        logger = LoggerMock2(('Hello, world!', 'INFO'))
        self.syslog.register_logger(logger)
        self.syslog.output_file('name', 'path')
        self.syslog.close()
        assert_equals(logger.output_file, ('name', 'path'))
        assert_true(logger.closed)

    def test_registered_logger_does_not_need_all_methods(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        self.syslog.register_logger(logger)
        self.syslog.output_file('name', 'path')
        self.syslog.close()

    def test_close_removes_registered_loggers(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        logger2 = LoggerMock2(('Hello, world!', 'INFO'))
        self.syslog.register_logger(logger, logger2)
        self.syslog.close()
        assert_true(self.syslog._writers == 
                    self.syslog._output_filers == 
                    self.syslog._closers == [])

    def test_registering_file_logger_with_none_path_does_nothing(self):
        self.syslog.register_file_logger('None')
        assert_equals(len(self.syslog._writers), 0)



if __name__ == "__main__":
    unittest.main()

