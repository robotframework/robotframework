import unittest

from robot.utils.asserts import assert_equal, assert_true, assert_false

from robot.output.logger import Logger
from robot.output.loggerapi import LoggerApi
from robot.output.console.verbose import VerboseOutput


class MessageMock:

    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message


class LoggerMock:

    def __init__(self, *expected):
        self.expected = list(expected)
        self.logger = self

    def message(self, msg):
        exp_msg, exp_level = self.expected.pop(0)
        assert_equal(msg.level, exp_level)
        assert_equal(msg.message, exp_msg)
        self.msg = msg

    def copy(self):
        return LoggerMock(*self.expected)

    def close(self):
        pass


class LoggerMock2(LoggerMock, LoggerApi):

    def result_file(self, kind, path):
        self.result_file_args = (kind, path)

    def close(self):
        self.closed = True


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.logger = Logger(register_console_logger=False)

    def test_write_to_one_logger(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger)
        self.logger.write('Hello, world!', 'INFO')
        assert_true(logger.msg.timestamp.year >= 2023)

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
            assert_equal(logger.msg.message, msg)
            assert_equal(logger.msg.level, level)

    def test_all_methods(self):
        logger = LoggerMock2(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger)
        self.logger.output_file('out.xml')
        assert_equal(logger.result_file_args, ('Output', 'out.xml'))
        self.logger.log_file('log.html')
        assert_equal(logger.result_file_args, ('Log', 'log.html'))
        self.logger.close()
        assert_true(logger.closed)

    def test_close_removes_registered_loggers(self):
        logger = LoggerMock(('Hello, world!', 'INFO'))
        logger2 = LoggerMock2(('Hello, world!', 'INFO'))
        self.logger.register_logger(logger, logger2)
        self.logger.close()
        assert_equal(self.logger._other_loggers, [])

    def test_registering_syslog_with_none_path_does_nothing(self):
        self.logger.register_syslog('None')
        assert_equal(self.logger._syslog, None)

    def test_cached_messages_are_given_to_registered_writers(self):
        self.logger.write('This is a cached message', 'INFO')
        self.logger.write('Another cached message', 'TRACE')
        logger = LoggerMock(('This is a cached message', 'INFO'),
                            ('Another cached message', 'TRACE'))
        self.logger.register_logger(logger)
        assert_equal(logger.msg.message, 'Another cached message')

    def test_message_cache_can_be_turned_off(self):
        self.logger.disable_message_cache()
        self.logger.write('This message is not cached', 'INFO')
        logger = LoggerMock(('', ''))
        self.logger.register_logger(logger)
        assert_false(hasattr(logger, 'msg'))

    def test_start_and_end_suite_test_and_keyword(self):
        class MyLogger(LoggerApi):
            def start_suite(self, suite, result): self.started_suite = suite
            def end_suite(self, suite, result): self.ended_suite = suite
            def start_test(self, test, result): self.started_test = test
            def end_test(self, test, result): self.ended_test = test
            def start_keyword(self, keyword, result): self.started_keyword = keyword
            def end_keyword(self, keyword, result): self.ended_keyword = keyword
        class Arg:
            type = None
            tests = ()
            suites = ()
            test_count = 0
        logger = MyLogger()
        self.logger.register_logger(logger)
        for name in 'suite', 'test', 'keyword':
            arg = Arg()
            arg.result = arg
            for stend in 'start', 'end':
                getattr(self.logger, stend + '_' + name)(arg, arg)
                assert_equal(getattr(logger, stend + 'ed_' + name), arg)

    def test_verbose_console_output_is_automatically_registered(self):
        logger = Logger()
        start_suite = logger._console_logger.start_suite
        assert_true(start_suite.__self__.__class__ is VerboseOutput)

    def test_automatic_console_logger_can_be_disabled(self):
        logger = Logger()
        logger.unregister_console_logger()
        assert_equal(logger._console_logger, None)
        self._number_of_registered_loggers_should_be(0, logger)

    def test_automatic_console_logger_can_be_disabled_after_registering_logger(self):
        logger = Logger()
        mock = LoggerMock()
        logger.register_logger(mock)
        self._number_of_registered_loggers_should_be(2, logger)
        logger.unregister_console_logger()
        self._number_of_registered_loggers_should_be(1, logger)

    def test_disabling_automatic_logger_multiple_times_has_no_effect(self):
        logger = Logger()
        logger.unregister_console_logger()
        self._number_of_registered_loggers_should_be(0, logger)
        logger.unregister_console_logger()
        logger.unregister_console_logger()
        self._number_of_registered_loggers_should_be(0, logger)
        logger.register_logger(LoggerMock())
        logger.unregister_console_logger()
        self._number_of_registered_loggers_should_be(1, logger)

    def test_registering_console_logger_disables_automatic_console_logger(self):
        logger = Logger()
        logger.register_console_logger(width=42)
        self._number_of_registered_loggers_should_be(1, logger)
        assert_equal(logger._console_logger.start_suite.__self__.writer.width, 42)

    def test_unregister_logger(self):
        logger1, logger2, logger3 = LoggerMock(), LoggerMock(), LoggerMock()
        self.logger.register_logger(logger1, logger2, logger3)
        self.logger.unregister_logger(logger2)
        self._number_of_registered_loggers_should_be(2)
        self.logger.unregister_logger(logger3, logger1)
        self._number_of_registered_loggers_should_be(0)

    def test_unregistering_non_registered_logger_is_ok(self):
        logger1, logger2 = LoggerMock(), LoggerMock()
        self.logger.register_logger(logger1)
        self.logger.unregister_logger(logger2)
        self.logger.unregister_logger(None)

    def test_start_and_end_loggers_and_iter(self):
        logger = Logger()
        xml = LoggerMock()
        listener = LoggerMock()
        lib_listener = LoggerMock()
        other = LoggerMock()
        logger.register_xml_logger(xml)
        logger.register_listeners(listener, lib_listener)
        logger.register_logger(other)
        assert_equal([proxy.logger for proxy in logger.start_loggers if not isinstance(proxy, LoggerApi)],
                     [other, xml, listener, lib_listener])
        assert_equal([proxy.logger for proxy in logger.end_loggers if not isinstance(proxy, LoggerApi)],
                     [listener, lib_listener, xml, other])
        assert_equal(list(logger), list(logger.end_loggers))

    def _number_of_registered_loggers_should_be(self, number, logger=None):
        logger = logger or self.logger
        assert_equal(len(list(logger)), number)


if __name__ == "__main__":
    unittest.main()
