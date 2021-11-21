from robot.api import SuiteVisitor


class NullishStarttimeModifier(SuiteVisitor):
    def __init__(self, nullish_label: str):
        self.stime_mod = nullish_label
         
    def visit_suite(self, suite):
        if self.stime_mod.lower() == 'none':
            suite.starttime = None
        elif self.stime_mod.lower() == 'empty':
            suite.starttime = ''
