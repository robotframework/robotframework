import unittest
from os.path import dirname, join

from robot.result import ExecutionResult
from robot.model import SuiteVisitor, TestSuite
from robot.utils.asserts import assert_equal


RESULT = ExecutionResult(join(dirname(__file__), 'golden.xml'))


class TestVisitingSuite(unittest.TestCase):

    def setUp(self):
        self.suite = suite = TestSuite()
        suite.setup.config(name='SS')
        suite.teardown.config(name='ST')
        test = suite.tests.create()
        test.setup.config(name='TS')
        test.teardown.config(name='TT')
        kw = test.body.create_keyword()
        kw.teardown.config(name='KT')

    def test_abstract_visitor(self):
        RESULT.suite.visit(SuiteVisitor())
        RESULT.suite.visit(SuiteVisitor())

    def test_start_suite_can_stop_visiting(self):
        RESULT.suite.visit(StartSuiteStopping())

    def test_start_test_can_stop_visiting(self):
        RESULT.suite.visit(StartTestStopping())

    def test_start_keyword_can_stop_visiting(self):
        RESULT.suite.visit(StartKeywordStopping())

    def test_visit_setups_and_teardowns(self):
        visitor = VisitSetupsAndTeardowns()
        self.suite.visit(visitor)
        assert_equal(visitor.visited, ['SS', 'TS', 'KT', 'TT', 'ST'])

    def test_dont_visit_inactive_setups_and_teardowns(self):
        suite = TestSuite()
        suite.tests.create().body.create_keyword()
        visitor = VisitSetupsAndTeardowns()
        suite.visit(visitor)
        assert_equal(visitor.visited, [])

    def test_visit_for(self):
        class VisitFor(SuiteVisitor):
            in_for = False

            def start_for(self, for_):
                for_.variables = ['${y}']
                for_.flavor = 'IN RANGE'
                self.in_for = True

            def end_for(self, for_):
                for_.values = ['10']
                self.in_for = False

            def start_keyword(self, keyword):
                if self.in_for:
                    keyword.name = 'IN FOR'

        for_ = self.suite.tests[0].body.create_for(['${x}'], 'IN', ['a', 'b', 'c'])
        kw = for_.body.create_keyword(name='K')
        self.suite.visit(VisitFor())
        assert_equal(str(for_), 'FOR    ${y}    IN RANGE    10')
        assert_equal(kw.name, 'IN FOR')

    def test_visit_if(self):
        class VisitIf(SuiteVisitor):
            level = None

            def start_if(self, if_):
                self.level = 0

            def start_if_branch(self, branch):
                self.level += 1
                branch.body.create_keyword()

            def end_if_branch(self, branch):
                if branch.type != branch.ELSE:
                    branch.condition = 'x > %d' % self.level

            def end_if(self, if_):
                self.level = None

            def start_keyword(self, keyword):
                if self.level is not None:
                    keyword.name = 'kw %d' % self.level

        if_ = self.suite.tests[0].body.create_if()
        branch1 = if_.body.create_branch(if_.IF, condition='xxx')
        branch2 = if_.body.create_branch(if_.ELSE_IF, condition='yyy')
        branch3 = if_.body.create_branch(if_.ELSE)
        self.suite.visit(VisitIf())
        assert_equal(branch1.condition, 'x > 1')
        assert_equal(branch1.body[0].name, 'kw 1')
        assert_equal(branch2.condition, 'x > 2')
        assert_equal(branch2.body[0].name, 'kw 2')
        assert_equal(branch3.condition, None)
        assert_equal(branch3.body[0].name, 'kw 3')

    def test_start_and_end_methods_can_add_items(self):
        suite = RESULT.suite.deepcopy()
        suite.visit(ItemAdder())
        assert_equal(len(suite.tests), len(RESULT.suite.tests) + 2)
        assert_equal(suite.tests[-2].name, 'Added by start_test')
        assert_equal(suite.tests[-1].name, 'Added by end_test')
        assert_equal(len(suite.tests[0].body),
                     len(RESULT.suite.tests[0].body) + 2)
        assert_equal(suite.tests[0].body[-2].name, 'Added by start_keyword')
        assert_equal(suite.tests[0].body[-1].name, 'Added by end_keyword')


class StartSuiteStopping(SuiteVisitor):

    def start_suite(self, suite):
        return False

    def end_suite(self, suite):
        raise AssertionError

    def start_test(self, test):
        raise AssertionError

    def start_keyword(self, keyword):
        raise AssertionError


class StartTestStopping(SuiteVisitor):

    def __init__(self):
        self.test_started = False

    def start_test(self, test):
        self.test_started = True
        return False

    def end_test(self, test):
        raise AssertionError

    def start_keyword(self, keyword):
        if self.test_started:
            raise AssertionError


class StartKeywordStopping(SuiteVisitor):

    def start_keyword(self, test):
        return False

    def end_keyword(self, test):
        raise AssertionError

    def log_message(self, msg):
        raise AssertionError


class VisitSetupsAndTeardowns(SuiteVisitor):

    def __init__(self):
        self.visited = []

    def start_keyword(self, keyword):
        if keyword.type in (keyword.SETUP, keyword.TEARDOWN):
            self.visited.append(keyword.name)


class ItemAdder(SuiteVisitor):
    test_to_add = 2
    test_started = False
    kw_added = False

    def start_test(self, test):
        if self.test_to_add > 0:
            test.parent.tests.create(name='Added by start_test')
            self.test_to_add -= 1
        self.test_started = True

    def end_test(self, test):
        if self.test_to_add > 0:
            test.parent.tests.create(name='Added by end_test')
            self.test_to_add -= 1
        self.test_started = False

    def start_keyword(self, keyword):
        if self.test_started and not self.kw_added:
            keyword.parent.body.create_keyword(kwname='Added by start_keyword')
            self.kw_added = True

    def end_keyword(self, keyword):
        if keyword.name == 'Added by start_keyword':
            keyword.parent.body.create_keyword(kwname='Added by end_keyword')


if __name__ == '__main__':
    unittest.main()
