"""Pre-run modifier that excludes tests by their name.

Tests to exclude are specified by using a pattern that is both case and space
insensitive and supports '*' (match anything) and '?' (match single character)
as wildcards.
"""

from robot.api import SuiteVisitor
from robot.utils import Matcher


class ExcludeTests(SuiteVisitor):

    def __init__(self, pattern):
        self.matcher = Matcher(pattern)

    def start_suite(self, suite):
        """Remove tests that match the given pattern."""
        suite.tests = [t for t in suite.tests if not self._is_excluded(t)]

    def _is_excluded(self, test):
        return self.matcher.match(test.name) or self.matcher.match(test.longname)

    def end_suite(self, suite):
        """Remove suites that are empty after removing tests."""
        suite.suites = [s for s in suite.suites if s.test_count > 0]

    def visit_test(self, test):
        """Avoid visiting tests and their keywords to save a little time."""
        pass
