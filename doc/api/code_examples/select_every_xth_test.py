from robot.api import SuiteVisitor


class SelectEveryXthTest(SuiteVisitor):
    """Visitor that keeps only every Xth test in the visited suite structure."""

    def __init__(self, x, start=0):
        self.x = int(x)
        self.start = int(start)

    def start_suite(self, suite):
        """Modify suite's tests to contain only every Xth."""
        suite.tests = suite.tests[self.start::self.x]

    def end_suite(self, suite):
        """Remove suites that are empty after removing tests."""
        suite.suites = [s for s in suite.suites if s.test_count > 0]

    def visit_test(self, test):
        """Save time to avoid visiting tests and their keywords."""
        pass
