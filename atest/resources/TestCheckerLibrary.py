import os
import re

from robot import utils
from robot.utils.asserts import assert_equals
from robot.result.resultbuilder import ExecutionResultBuilder
from robot.result.executionresult import Result
from robot.result.testsuite import TestSuite
from robot.result.testcase import TestCase
from robot.result.keyword import Keyword
from robot.libraries.BuiltIn import BuiltIn


class NoSlotsKeyword(Keyword):
    pass

class NoSlotsTestCase(TestCase):
    keyword_class = NoSlotsKeyword

class NoSlotsTestSuite(TestSuite):
    test_class = NoSlotsTestCase
    keyword_class = NoSlotsKeyword


class TestCheckerLibrary:

    def process_output(self, path):
        path = path.replace('/', os.sep)
        try:
            print "Processing output '%s'" % path
            result = Result(root_suite=NoSlotsTestSuite())
            ExecutionResultBuilder(path).build(result)
        except:
            raise RuntimeError('Processing output failed: %s'
                               % utils.get_error_message())
        setter = BuiltIn().set_suite_variable
        setter('$SUITE', process_suite(result.suite))
        setter('$STATISTICS', result.statistics)
        setter('$ERRORS', process_errors(result.errors))

    def get_test_from_suite(self, suite, name):
        tests = self.get_tests_from_suite(suite, name)
        if len(tests) == 1:
            return tests[0]
        err = "No test '%s' found from suite '%s'" if not tests \
            else "More than one test '%s' found from suite '%s'"
        raise RuntimeError(err % (name, suite.name))

    def get_tests_from_suite(self, suite, name=None):
        tests = [test for test in suite.tests
                 if name is None or utils.eq(test.name, name)]
        for subsuite in suite.suites:
            tests.extend(self.get_tests_from_suite(subsuite, name))
        return tests

    def get_suite_from_suite(self, suite, name):
        suites = self.get_suites_from_suite(suite, name)
        if len(suites) == 1:
            return suites[0]
        err = "No suite '%s' found from suite '%s'" if not suites \
            else "More than one suite '%s' found from suite '%s'"
        raise RuntimeError(err % (name, suite.name))

    def get_suites_from_suite(self, suite, name):
        suites = [suite] if utils.eq(suite.name, name) else []
        for subsuite in suite.suites:
            suites.extend(self.get_suites_from_suite(subsuite, name))
        return suites

    def check_test_status(self, test, status=None, message=None):
        """Verifies that test's status and message are as expected.

        Expected status and message can be given as parameters. If expected
        status is not given, expected status and message are read from test's
        documentation. If documentation doesn't contain any of PASS, FAIL or
        ERROR, test's status is expected to be PASS. If status is given that is
        used. Expected message is documentation after given status. Expected
        message can also be regular expression. In that case expected match
        starts with REGEXP: , which is ignored in the regexp match.
        """
        if status is not None:
            test.exp_status = status
        if message is not None:
            test.exp_message = message
        if test.exp_status != test.status:
            if test.exp_status == 'PASS':
                msg = "Test was expected to PASS but it FAILED. "
                msg += "Error message:\n" + test.message
            else:
                msg = "Test was expected to FAIL but it PASSED. "
                msg += "Expected message:\n" + test.exp_message
            raise AssertionError(msg)
        if test.exp_message == test.message:
            return
        if test.exp_message.startswith('REGEXP:'):
            pattern = test.exp_message.replace('REGEXP:', '', 1).strip()
            if re.match('^%s$' % pattern, test.message, re.DOTALL):
                return
        if test.exp_message.startswith('GLOB:'):
            pattern = test.exp_message.replace('GLOB:', '', 1).strip()
            matcher = utils.Matcher(pattern, caseless=False, spaceless=False)
            if matcher.match(test.message):
                return
        if test.exp_message.startswith('STARTS:'):
            start = test.exp_message.replace('STARTS:', '', 1).strip()
            if not start:
                raise RuntimeError("Empty 'STARTS:' is not allowed")
            if test.message.startswith(start):
                return
        raise AssertionError("Wrong message\n\n"
                             "Expected:\n%s\n\nActual:\n%s\n"
                             % (test.exp_message, test.message))

    def check_suite_contains_tests(self, suite, *expected_names, **statuses):
        actual_tests = [test for test in self.get_tests_from_suite(suite)]
        tests_msg = """
Expected tests : %s
Actual tests   : %s""" % (str(list(expected_names)), str(actual_tests))
        expected_names = [utils.normalize(name) for name in expected_names]
        statuses = dict((utils.normalize(k), v) for k, v in statuses.items())
        if len(actual_tests) != len(expected_names):
            raise AssertionError("Wrong number of tests." + tests_msg)
        for test in actual_tests:
            norm_name = utils.normalize(test.name)
            if utils.MultiMatcher(expected_names).match(test.name):
                print "Verifying test '%s'" % test.name
                status = statuses.get(norm_name)
                if status and ':' in status:
                    status, message = status.split(':', 1)
                else:
                    message = None
                self.check_test_status(test, status, message)
                expected_names.remove(norm_name)
            else:
                raise AssertionError("Test '%s' was not expected to be run.%s"
                                     % (test.name, tests_msg))
        assert not expected_names

    def should_contain_tests(self, suite, *test_names):
        self.check_suite_contains_tests(suite, *test_names)

    def should_not_contain_tests(self, suite, *test_names):
        actual_names = [t.name for t in suite.tests]
        for name in test_names:
            if name in actual_names:
                raise AssertionError('Suite should not have contained test "%s"' % name)

    def should_contain_suites(self, suite, *expected_names):
        print 'Suite has suites', suite.suites
        actual_names = [s.name for s in suite.suites]
        assert_equals(len(actual_names), len(expected_names), 'Wrong number of subsuites')
        for expected in expected_names:
            if not utils.Matcher(expected).match_any(actual_names):
                raise AssertionError('Suite %s not found' % expected)

    def should_contain_tags(self, test, *tags):
        print 'Test has tags', test.tags
        assert_equals(len(test.tags), len(tags), 'Wrong number of tags')
        tags = sorted(tags, key=lambda s: s.lower().replace('_', '').replace(' ', ''))
        for act, exp in zip(test.tags, tags):
            assert_equals(act, exp)

    def should_contain_keywords(self, item, *kw_names):
        actual_names = [kw.name for kw in item.keywords]
        assert_equals(len(actual_names), len(kw_names), 'Wrong number of keywords')
        for act, exp in zip(actual_names, kw_names):
            assert_equals(act, exp)

    def test_should_have_correct_keywords(self, *kw_names, **config):
        get_var = BuiltIn().get_variable_value
        suite = get_var('${SUITE}')
        name = config.get('name', get_var('${TEST NAME}'))
        kw_index = int(config.get('kw_index', 0))
        test = self.get_test_from_suite(suite, name)
        self.check_test_status(test)
        self.should_contain_keywords(test.keywords[kw_index], *kw_names)
        return test


def process_suite(suite):
    for subsuite in suite.suites:
        process_suite(subsuite)
    for test in suite.tests:
        process_test(test)
    for kw in suite.keywords:
        process_keyword(kw)
    suite.setup = suite.keywords.setup
    suite.teardown = suite.keywords.teardown
    return suite

def process_test(test):
    if 'FAIL' in test.doc:
        test.exp_status = 'FAIL'
        test.exp_message = test.doc.split('FAIL', 1)[1].lstrip()
    else:
        test.exp_status = 'PASS'
        test.exp_message = '' if 'PASS' not in test.doc else test.doc.split('PASS', 1)[1].lstrip()
    for kw in test.keywords:
        process_keyword(kw)
    test.setup = test.keywords.setup
    test.teardown = test.keywords.teardown
    test.keywords = test.kws = list(test.keywords.normal)
    test.keyword_count = test.kw_count = len(test.keywords)

def process_keyword(kw):
    if kw is None:
        return
    kw.kws = kw.keywords
    kw.msgs = kw.messages
    kw.message_count = kw.msg_count = len(kw.messages)
    kw.keyword_count = kw.kw_count = len(list(kw.keywords.normal))
    for subkw in kw.keywords:
        process_keyword(subkw)

def process_errors(errors):
    errors.msgs = errors.messages
    errors.message_count = errors.msg_count = len(errors.messages)
    return errors
