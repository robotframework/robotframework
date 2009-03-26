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
        assert_equals(self.syslog._loggers, [])

    def test_registering_file_logger_with_none_path_does_nothing(self):
        self.syslog.register_file_logger('None')
        assert_equals(self.syslog._loggers, [])

    def test_cached_messages_are_given_to_registered_writers(self):
        self.syslog.write('This is a cached message', 'INFO')
        self.syslog.write('Another cached message', 'TRACE')
        logger = LoggerMock(('This is a cached message', 'INFO'), 
                            ('Another cached message', 'TRACE'))
        self.syslog.register_logger(logger)
        assert_equals(logger.msg.message, 'Another cached message')

    def test_message_cache_can_be_turned_off(self):
        self.syslog.disable_message_cache()
        self.syslog.write('This message is not cached', 'INFO')
        logger = LoggerMock(('', ''))
        self.syslog.register_logger(logger)
        assert_false(hasattr(logger, 'msg'))

    def test_start_and_end_suite_test_and_keyword(self):
        class Logger:
            def start_suite(self, suite): self.started_suite = suite
            def end_suite(self, suite): self.ended_suite = suite
            def start_test(self, test): self.started_test = test
            def end_test(self, test): self.ended_test = test
            def start_keyword(self, keyword): self.started_keyword = keyword
            def end_keyword(self, keyword): self.ended_keyword = keyword
        logger = Logger()
        self.syslog.register_logger(logger)
        for name in 'suite', 'test', 'keyword':
            for stend in 'start', 'end':
                getattr(self.syslog, stend+'_'+name)(name)
                assert_equals(getattr(logger, stend+'ed_'+name), name)


if __name__ == "__main__":
    unittest.main()

