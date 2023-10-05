import unittest

from robot.result import TestSuite
from robot.result.keywordremover import WaitUntilKeywordSucceedsRemover
from robot.utils.asserts import assert_equal


class TestWUKSRemover(unittest.TestCase):

    def test_empty(self):
        self._assert_removed()

    def test_one_passing(self):
        self._assert_removed(passing=1, expected=1)

    def test_one_failing(self):
        self._assert_removed(failing=1, expected=1)

    def test_failing_and_passing(self):
        self._assert_removed(failing=1, passing=1, expected=2)
        self._assert_removed(failing=9, passing=1, expected=2)

    def test_only_messages(self):
        self._assert_removed(messages=1, expected=1)
        self._assert_removed(messages=7, expected=7)

    def test_keywords_and_messages(self):
        self._assert_removed(passing=1, messages=1, expected=2)
        self._assert_removed(failing=1, messages=2, expected=3)
        self._assert_removed(failing=1, passing=1, messages=2, expected=4)
        self._assert_removed(failing=9, passing=1, messages=3, expected=5)

    def _assert_removed(self, failing=0, passing=0, messages=0, expected=0):
        suite = TestSuite()
        kw = suite.tests.create().body.create_keyword(
            owner='BuiltIn', name='Wait Until Keyword Succeeds'
        )
        for i in range(failing):
            kw.body.create_keyword(status='FAIL')
        for i in range(passing):
            kw.body.create_keyword(status='PASS')
        for i in range(messages):
            kw.body.create_message()
        suite.visit(WaitUntilKeywordSucceedsRemover())
        assert_equal(len(kw.body), expected)


if __name__ == '__main__':
    unittest.main()
