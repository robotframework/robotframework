import unittest

from robot.utils.asserts import assert_equals
from robot.common.model import BaseTestSuite


class Suite(BaseTestSuite):
    def __init__(self, parent=None):
        BaseTestSuite.__init__(self, 'name', parent=parent)


class TestSuiteId(unittest.TestCase):

    def test_one_suite(self):
        assert_equals(Suite().id, 's1')

    def test_sub_suites(self):
        parent = Suite()
        for i in range(10):
            assert_equals(Suite(parent).id, 's1-s%s' % (i+1))
        assert_equals(Suite(Suite(parent)).id, 's1-s11-s1')

if __name__ == '__main__':
    unittest.main()
