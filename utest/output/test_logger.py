import unittest

from robot.utils.asserts import *

from robot.output.logger import _Logger, CommandLineMonitor


class MessageMock:
    
    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message
    
class LoggerMock:

    def __init__(self, *expected):
        self.expected = list(expected)
    
    def message(self, msg):
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


class TestLogger(unittest.TestCase):
    
    def setUp(self):
        self.logger = _Logger()
        self.logger.disable_automatic_console_logger()

    def test_write_to_one_logger(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger)
        self.logger.write('Hello, world!', 'INFO')
        assert_true(logger.msg.timestamp.startswith('20'))
        
    def test_write_to_one_logger_with_trace_level(self):
        logger = LoggerMock(('expected message', 'TRACE'))
        self.logger.register_logger(logger)
        self.logger.write('expected message', 'TRACE')
        assert_true(hasattr(logger, 'msg'))
    
    def test_write_to_multiple_loggers(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        logger2 = logger.copy()
        logger3 = logger.copy()
        self.logger.register_logger(logger, logger2, logger3)
        self.logger.message(MessageMock('', 'INFO', 'Hello, world!'))
        assert_true(logger.msg is logger2.msg)
        assert_true(logger.msg is logger.msg)

    def test_write_multiple_messages(self):
        msgs = [('0', 'ERROR'), ('1', 'WARN'), ('2', 'INFO'), ('3', 'DEBUG'), ('4', 'TRACE')]
        logger = LoggerMock(*msgs)
        self.logger.register_logger(logger)
        for msg, level in msgs:
            self.logger.write(msg, level)
            assert_equals(logger.msg.message, msg)
            assert_equals(logger.msg.level, level)
        
    def test_all_methods(self):
        logger = LoggerMock2(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger)
        self.logger.output_file('name', 'path')
        self.logger.close()
        assert_equals(logger.output_file, ('name', 'path'))
        assert_true(logger.closed)

    def test_registered_logger_does_not_need_all_methods(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger)
        self.logger.output_file('name', 'path')
        self.logger.close()

    def test_close_removes_registered_loggers(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        logger2 = LoggerMock2(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger, logger2)
        self.logger.close()
        assert_equals(self.logger._loggers, [])

    def test_registering_file_logger_with_none_path_does_nothing(self):
        self.logger.register_file_logger('None')
        assert_equals(self.logger._loggers, [])

    def test_cached_messages_are_given_to_registered_writers(self):
        self.logger.write('This is a cached message', 'INFO')
        self.logger.write('Another cached message', 'TRACE')
        logger = LoggerMock(('This is a cached message', 'INFO'), 
                            ('Another cached message', 'TRACE'))
        self.logger.register_logger(logger)
        assert_equals(logger.msg.message, 'Another cached message')

    def test_message_cache_can_be_turned_off(self):
        self.logger.disable_message_cache()
        self.logger.write('This message is not cached', 'INFO')
        logger = LoggerMock(('', ''))
        self.logger.register_logger(logger)
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
        self.logger.register_logger(logger)
        for name in 'suite', 'test', 'keyword':
            for stend in 'start', 'end':
                getattr(self.logger, stend+'_'+name)(name)
                assert_equals(getattr(logger, stend+'ed_'+name), name)

    def test_console_logger_is_automatically_registered(self):
        logger = _Logger()
        assert_true(logger._loggers[0].start_suite.im_class is CommandLineMonitor) 

    def test_automatic_console_logger_can_be_disabled(self):
        logger = _Logger()
        logger.disable_automatic_console_logger()
        assert_equals(logger._loggers, [])

    def test_automatic_console_logger_can_be_disabled(self):
        logger = _Logger()
        mock = LoggerMock()
        logger.register_logger(mock)
        logger.disable_automatic_console_logger()
        assert_equals(len(logger._loggers), 1)
        assert_true(logger._loggers[0].message.im_class is LoggerMock) 

    def test_disabling_automatic_logger_multiple_times_has_no_effect(self):
        logger = _Logger()
        logger.disable_automatic_console_logger()
        assert_equals(len(logger._loggers), 0)
        logger.disable_automatic_console_logger()
        logger.disable_automatic_console_logger()
        assert_equals(len(logger._loggers), 0)
        logger.register_logger(LoggerMock())
        logger.disable_automatic_console_logger()
        assert_equals(len(logger._loggers), 1)

    def test_reigstering_console_logger_disables_automatic_console_logger(self):
        logger = _Logger()
        logger.register_console_logger(width=42)
        assert_equals(len(logger._loggers), 1)
        assert_equals(logger._loggers[0].start_suite.im_self._width, 42)

    def test_unregister_logger(self):
        logger1, logger2, logger3 = LoggerMock(), LoggerMock(), LoggerMock()
        self.logger.register_logger(logger1, logger2, logger3)
        self.logger.unregister_logger(logger2)
        assert_equals(len(self.logger._loggers), 2)
        self.logger.unregister_logger(logger3, logger1)
        assert_equals(len(self.logger._loggers), 0)

    def test_unregistering_non_registered_logger_is_ok(self):
        logger1, logger2 = LoggerMock(), LoggerMock()
        self.logger.register_logger(logger1)
        self.logger.unregister_logger(logger2)
        self.logger.unregister_logger(None)


if __name__ == "__main__":
    unittest.main()

