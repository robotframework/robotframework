from robot.model import SuiteVisitor


class ModelModifier(SuiteVisitor):

    def __init__(self, *tags):
        self.config = tags or ('visited',)

    def start_suite(self, suite):
        if self.config[0] == 'FAIL':
            raise RuntimeError(' '.join(self.config[1:]))
        if self.config == ('REMOVE', 'ALL', 'TESTS'):
            suite.tests = []
        else:
            suite.tests = [t for t in suite.tests if not t.tags.match('fail')]

    def visit_test(self, test):
        test.tags.add(self.config)
