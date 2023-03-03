import unittest

from robot.utils.asserts import assert_equal, assert_raises_with_msg
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.libraries.DateTime import Date


class TestBuiltInWhenRobotNotRunning(unittest.TestCase):

    def test_using_namespace(self):
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().get_variables)

    def test_using_namespace_backwards_compatibility(self):
        assert_raises_with_msg(AttributeError,
                               'Cannot access execution context',
                               BuiltIn().get_variables)

    def test_suite_doc_and_metadata(self):
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().set_suite_documentation, 'value')
        assert_raises_with_msg(RobotNotRunningError,
                               'Cannot access execution context',
                               BuiltIn().set_suite_metadata, 'name', 'value')


class TestBuiltInPropertys(unittest.TestCase):

    def test_robot_running(self):
        assert_equal(BuiltIn().robot_running, False)

    def test_dry_run_active(self):
        assert_equal(BuiltIn().dry_run_active, False)


class TestDateTime(unittest.TestCase):

    def test_date_seconds(self):
        secs = 1234567890
        assert_equal(Date(secs).seconds, secs)


if __name__ == '__main__':
    unittest.main()
