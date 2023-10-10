import unittest
from os.path import dirname, join

from robot.api.parsing import get_model
from robot.result import ExecutionResult
from robot.model import SuiteVisitor, TestSuite
from robot.result import TestSuite as ResultSuite
from robot.running import TestSuite as RunningSuite
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
        test.body.create_keyword()

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
        assert_equal(visitor.visited, ['SS', 'TS', 'TT', 'ST'])

    def test_visit_keyword_setup_and_teardown(self):
        suite = ResultSuite()
        suite.setup.config(name='SS')
        suite.teardown.config(name='ST')
        test = suite.tests.create()
        test.setup.config(name='TS')
        test.teardown.config(name='TT')
        kw = test.body.create_keyword()
        kw.setup.config(name='KS')
        kw.teardown.config(name='KT')
        visitor = VisitSetupsAndTeardowns()
        suite.visit(visitor)
        assert_equal(visitor.visited, ['SS', 'TS', 'KS', 'KT', 'TT', 'ST'])

    def test_dont_visit_inactive_setups_and_teardowns(self):
        suite = ResultSuite()
        suite.tests.create().body.create_keyword()
        visitor = VisitSetupsAndTeardowns()
        suite.visit(visitor)
        assert_equal(visitor.visited, [])

    def test_visit_for(self):
        class VisitFor(SuiteVisitor):
            in_for = False

            def start_for(self, for_):
                for_.assign = ['${y}']
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

    def test_start_end_body_item(self):
        class Visitor(SuiteVisitor):
            def __init__(self):
                self.visited = []

            def start_body_item(self, item):
                self.visited.append(f'START {item.type}')

            def end_body_item(self, item):
                self.visited.append(f'END {item.type}')

        visitor = Visitor()
        RunningSuite.from_model(get_model('''
*** Test Cases ***
Example
    IF    True
        WHILE    True
            BREAK
        END
    ELSE IF    True
        FOR    ${x}    IN    @{stuff}
            CONTINUE
        END
    ELSE
        TRY
            Keyword
        EXCEPT    Something
            Keyword
        ELSE
            Keyword
        FINALLY
            Keyword
        END
    END
''')).visit(visitor)
        expected = '''
START IF/ELSE ROOT
    START IF
        START WHILE
            START BREAK
            END BREAK
        END WHILE
    END IF
    START ELSE IF
        START FOR
            START CONTINUE
            END CONTINUE
        END FOR
    END ELSE IF
    START ELSE
        START TRY/EXCEPT ROOT
            START TRY
                START KEYWORD
                END KEYWORD
            END TRY
            START EXCEPT
                START KEYWORD
                END KEYWORD
            END EXCEPT
            START ELSE
                START KEYWORD
                END KEYWORD
            END ELSE
            START FINALLY
                START KEYWORD
                END KEYWORD
            END FINALLY
        END TRY/EXCEPT ROOT
    END ELSE
END IF/ELSE ROOT
'''.strip().splitlines()
        assert_equal(visitor.visited, [e.strip() for e in expected])

    def test_visit_return_continue_and_break(self):
        suite = ResultSuite()
        suite.tests.create().body.create_return().body.create_keyword(name='R')
        suite.tests.create().body.create_continue().body.create_message(message='C')
        suite.tests.create().body.create_break().body.create_keyword(name='B')

        class Visitor(SuiteVisitor):
            visited_return = visited_continue = visited_break = False
            visited_return_body = visited_continue_body = visited_break_body = False

            def start_return(self, return_):
                self.visited_return = True

            def end_continue(self, continue_):
                self.visited_continue = True

            def start_break(self, break_):
                self.visited_break = True

            def start_keyword(self, keyword):
                if keyword.name == 'R':
                    self.visited_return_body = True
                if keyword.name == 'B':
                    self.visited_break_body = True

            def visit_message(self, msg):
                if msg.message == 'C':
                    self.visited_continue_body = True

        visitor = Visitor()
        suite.visit(visitor)
        for visited in 'return', 'continue', 'break':
            assert_equal(getattr(visitor, f'visited_{visited}'), True, visited)
            assert_equal(getattr(visitor, f'visited_{visited}_body'), True, f'{visited}_body')


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
            keyword.parent.body.create_keyword(name='Added by start_keyword')
            self.kw_added = True

    def end_keyword(self, keyword):
        if keyword.name == 'Added by start_keyword':
            keyword.parent.body.create_keyword(name='Added by end_keyword')


if __name__ == '__main__':
    unittest.main()
