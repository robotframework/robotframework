import unittest

from robot.utils.asserts import assert_equal, assert_true, assert_false

import robot.output.pyloggingconf as pyLogging

import logging


class MessageMock:
    def __init__(self, timestamp, level, message):
        self.timestamp = timestamp
        self.level = level
        self.message = message


class MockLibraryLogger:
    def __init__(self):
        self.last_message = (None, None)

    def error(self, message):
        self.last_message = (message, logging.ERROR)

    def warn(self, message):
        self.last_message = (message, logging.WARNING)

    def info(self, message):
        self.last_message = (message, logging.INFO)

    def debug(self, message):
        self.last_message = (message, logging.DEBUG)

    def trace(self, message):
        self.last_message = (message, logging.NOTSET)


class TestPyLogging(unittest.TestCase):
    def setUp(self):
        self.library_logger = MockLibraryLogger()
        self.test_handler = pyLogging.RobotHandler(library_logger=self.library_logger)
        root = logging.getLogger()
        root.setLevel(logging.NOTSET)
        for handler in root.handlers:
            root.removeHandler(handler)
        root.addHandler(self.test_handler)

    def tearDown(self):
        root = logging.getLogger()
        root.removeHandler(self.test_handler)

    def test_python_logging_debug(self):
        TESTMESSAGE = "This is a test message"
        logging.debug(TESTMESSAGE)
        message, level = self.library_logger.last_message
        assert_equal(message, TESTMESSAGE)
        assert_equal(level, logging.DEBUG)

    def test_python_logging_info(self):
        TESTMESSAGE = "This is a test message"
        logging.info(TESTMESSAGE)
        message, level = self.library_logger.last_message
        assert_equal(message, TESTMESSAGE)
        assert_equal(level, logging.INFO)

    def test_python_logging_warn(self):
        TESTMESSAGE = "This is a test message"
        logging.warning(TESTMESSAGE)
        message, level = self.library_logger.last_message
        assert_equal(message, TESTMESSAGE)
        assert_equal(level, logging.WARNING)

    def test_python_logging_error(self):
        TESTMESSAGE = "This is a test message"
        logging.error(TESTMESSAGE)
        message, level = self.library_logger.last_message
        assert_equal(message, TESTMESSAGE)
        assert_equal(level, logging.ERROR)

    def test_python_logging_formatted_debug(self):
        DEFAULTLOGGINGFORMAT = '%(name)s %(levelname)s %(message)s'
        DEFAULTLOGGINGDATEFORMAT = '%m/%d %H:%M:%S'
        TESTMESSAGE = "This is a test message"
        FORMATTEDMESSAGE = f"root DEBUG {TESTMESSAGE}"
        old_formatter = self.test_handler.formatter
        formatter = logging.Formatter(fmt=DEFAULTLOGGINGFORMAT)
        self.test_handler.setFormatter(formatter)

        logging.debug(TESTMESSAGE)
        
        message, level = self.library_logger.last_message
        assert_equal(message, FORMATTEDMESSAGE)
        assert_equal(level, logging.DEBUG)
        self.test_handler.setFormatter(old_formatter)

    def test_python_logging_formatted_info(self):
        DEFAULTLOGGINGFORMAT = '%(name)s %(levelname)s %(message)s'
        DEFAULTLOGGINGDATEFORMAT = '%m/%d %H:%M:%S'
        TESTMESSAGE = "This is a test message"
        FORMATTEDMESSAGE = f"root INFO {TESTMESSAGE}"
        old_formatter = self.test_handler.formatter
        formatter = logging.Formatter(fmt=DEFAULTLOGGINGFORMAT)
        self.test_handler.setFormatter(formatter)

        logging.info(TESTMESSAGE)
        
        message, level = self.library_logger.last_message
        assert_equal(message, FORMATTEDMESSAGE)
        assert_equal(level, logging.INFO)
        self.test_handler.setFormatter(old_formatter)

    def test_python_logging_formatted_warn(self):
        DEFAULTLOGGINGFORMAT = '%(name)s %(levelname)s %(message)s'
        DEFAULTLOGGINGDATEFORMAT = '%m/%d %H:%M:%S'
        TESTMESSAGE = "This is a test message"
        FORMATTEDMESSAGE = f"root WARNING {TESTMESSAGE}"
        old_formatter = self.test_handler.formatter
        formatter = logging.Formatter(fmt=DEFAULTLOGGINGFORMAT)
        self.test_handler.setFormatter(formatter)

        logging.warning(TESTMESSAGE)
        
        message, level = self.library_logger.last_message
        assert_equal(message, FORMATTEDMESSAGE)
        assert_equal(level, logging.WARNING)
        self.test_handler.setFormatter(old_formatter)

    def test_python_logging_formatted_error(self):
        DEFAULTLOGGINGFORMAT = '%(name)s %(levelname)s %(message)s'
        DEFAULTLOGGINGDATEFORMAT = '%m/%d %H:%M:%S'
        TESTMESSAGE = "This is a test message"
        FORMATTEDMESSAGE = f"root ERROR {TESTMESSAGE}"
        old_formatter = self.test_handler.formatter
        formatter = logging.Formatter(fmt=DEFAULTLOGGINGFORMAT)
        self.test_handler.setFormatter(formatter)

        logging.error(TESTMESSAGE)
        
        message, level = self.library_logger.last_message
        assert_equal(message, FORMATTEDMESSAGE)
        assert_equal(level, logging.ERROR)
        self.test_handler.setFormatter(old_formatter)
