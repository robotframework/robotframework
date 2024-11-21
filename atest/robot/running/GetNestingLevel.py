from robot.api import SuiteVisitor


class Nesting(SuiteVisitor):

    def __init__(self):
        self.level = 0
        self.max = 0

    def start_keyword(self, kw):
        self.level += 1
        self.max = max(self.level, self.max)

    def end_keyword(self, kw):
        self.level -= 1


def get_nesting_level(test):
    nesting = Nesting()
    test.visit(nesting)
    return nesting.max
