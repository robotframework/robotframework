import unittest

from robot.output.loggerhelper import Message
from robot.result import Message as ResultMessage
from robot.utils.asserts import assert_equal, assert_true


class TestMessage(unittest.TestCase):

    def test_string_message(self):
        assert_equal(Message("my message").message, "my message")

    def test_callable_message(self):
        assert_equal(Message(lambda: "my message").message, "my message")

    def test_correct_base_type(self):
        assert_true(isinstance(Message("msg"), ResultMessage))


if __name__ == "__main__":
    unittest.main()
