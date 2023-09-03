import unittest

from robot.utils.asserts import assert_equal, assert_raises_with_msg
from robot.model import TestSuite, Keyword
from robot.model.fixture import create_fixture


class TestCreateFixture(unittest.TestCase):

    def test_creates_default_fixture_when_given_none(self):
        suite = TestSuite()
        fixture = create_fixture(suite.fixture_class, None, suite, Keyword.SETUP)
        self._assert_fixture(fixture, suite, Keyword.SETUP)

    def test_sets_parent_and_type_correctly(self):
        suite = TestSuite()
        kw = Keyword('KW Name')
        fixture = create_fixture(suite.fixture_class, kw, suite, Keyword.TEARDOWN)
        self._assert_fixture(fixture, suite, Keyword.TEARDOWN)

    def test_raises_type_error_when_wrong_fixture_type(self):
        suite = TestSuite()
        wrong_kw = object()
        assert_raises_with_msg(
            TypeError, "Invalid fixture type 'object'.",
            create_fixture, suite.fixture_class, wrong_kw, suite, Keyword.TEARDOWN
        )

    def _assert_fixture(self, fixture, exp_parent, exp_type,
                        exp_class=TestSuite.fixture_class):
        assert_equal(fixture.parent, exp_parent)
        assert_equal(fixture.type, exp_type)
        assert_equal(fixture.__class__, exp_class)


if __name__ == '__main__':
    unittest.main()
