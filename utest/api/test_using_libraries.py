import unittest

from robot.utils.asserts import assert_raises_with_msg
from robot.libraries.BuiltIn import BuiltIn


class TestBuiltIn(unittest.TestCase):

    def test_error_when_using_namespace_and_robot_not_running(self):
        assert_raises_with_msg(AttributeError,
                               'Cannot access execution context when '
                               'Robot Framework is not running.',
                               BuiltIn().get_variables)


if __name__ == '__main__':
    unittest.main()
