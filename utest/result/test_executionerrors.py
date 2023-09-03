import unittest

from robot.result.executionerrors import ExecutionErrors, Message
from robot.utils.asserts import assert_equal


class TestExecutionErrors(unittest.TestCase):

    def test_str_without_messages(self):
        assert_equal(str(ExecutionErrors()), 'No execution errors')

    def test_str_with_one_message(self):
        assert_equal(str(ExecutionErrors([Message('Only one')])),
                     'Execution error: Only one')

    def test_str_with_multiple_messages(self):
        assert_equal(str(ExecutionErrors([Message('1st'), Message('2nd')])),
                     'Execution errors:\n- 1st\n- 2nd')


if __name__ == '__main__':
    unittest.main()
