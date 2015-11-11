import unittest

from robot.utils.asserts import assert_raises, assert_equal
from robot.errors import DataError
from robot.output.loggerhelper import AbstractLogger, Message


class TestAbstractLogger(unittest.TestCase):

    def test_set_invalid_threshold(self):
        logger = AbstractLogger('trace')
        assert_raises(DataError, logger.set_level, 'INVALID THRESHOLD')


class TestMessage(unittest.TestCase):

    def test_string_message(self):
        assert_equal(Message('my message').message, 'my message')

    def test_callable_message(self):
        assert_equal(Message(lambda: 'my message').message, 'my message')


if __name__ == '__main__':
    unittest.main()
