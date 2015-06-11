from robot.model import SuiteVisitor


class PreRunVisitor(SuiteVisitor):

    def __init__(self, *tags):
        self.tags = tags or ('visited',)

    def start_suite(self, suite):
        if self.tags[0] == 'FAIL':
            raise RuntimeError(' '.join(self.tags[1:]))
        suite.tests = [t for t in suite.tests if not t.tags.match('fail')]

    def visit_test(self, test):
        test.tags.add(self.tags)
