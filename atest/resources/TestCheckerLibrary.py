import os
import re

from robot import utils
from robot.utils.asserts import assert_equal
from robot.result import (ExecutionResultBuilder, Keyword, TestCase, TestSuite,
                          Result)
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
        set_suite_variable = BuiltIn().set_suite_variable
        if not path or path.upper() == 'NONE':
            set_suite_variable('$SUITE', None)
            print("Not processing output.")
            return
        path = path.replace('/', os.sep)
        try:
            print("Processing output '%s'." % path)
            result = Result(root_suite=NoSlotsTestSuite())
            ExecutionResultBuilder(path).build(result)
        except:
            set_suite_variable('$SUITE', None)
            raise RuntimeError('Processing output failed: %s'
                               % utils.get_error_message())
        set_suite_variable('$SUITE', process_suite(result.suite))
        set_suite_variable('$STATISTICS', result.statistics)
        set_suite_variable('$ERRORS', process_errors(result.errors))

    def get_test_case(self, name):
        suite = BuiltIn().get_variable_value('${SUITE}')
        return self._get_test_from_suite(suite, name)

    def _get_test_from_suite(self, suite, name):
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

    def get_test_suite(self, name):
        suite = BuiltIn().get_variable_value('${SUITE}')
        suites = self._get_suites_from_suite(suite, name)
        if len(suites) == 1:
            return suites[0]
        err = "No suite '%s' found from suite '%s'" if not suites \
            else "More than one suite '%s' found from suite '%s'"
        raise RuntimeError(err % (name, suite.name))

    def _get_suites_from_suite(self, suite, name):
        suites = [suite] if utils.eq(suite.name, name) else []
        for subsuite in suite.suites:
            suites.extend(self._get_suites_from_suite(subsuite, name))
        return suites

    def check_test_case(self, testname, status=None, message=None):
        test = self._get_test_from_suite(BuiltIn().get_variable_value('${SUITE}'), testname)
        self._check_test_status(test, status=status, message=message)
        return test

    def _check_test_status(self, test, status=None, message=None):
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

    def should_contain_tests(self, suite, *names, **names_and_statuses):
        """Verify that specified tests exists in suite.

        'names' contains test names to check. These tests are expected to
        pass/fail as their documentation says. Is same name is given multiple
        times, test ought to be executed multiple times too.

        'names_and_statuses' contains test names with associated custom status
        in format `STATUS:Message`. Test is given both in 'names' and in
        'names_and_statuses', only the latter has an effect.
        """
        tests = self.get_tests_from_suite(suite)
        expected = [(n, None) for n in names if n not in names_and_statuses]
        expected.extend((n, s) for n, s in names_and_statuses.items())
        tests_msg = "\nExpected tests : %s\nActual tests   : %s" \
                    % (', '.join(sorted([e[0] for e in expected], key=lambda s: s.lower())),
                       ', '.join(sorted([t.name for t in tests], key=lambda s: s.lower())))
        if len(tests) != len(expected):
            raise AssertionError("Wrong number of tests." + tests_msg)
        for test in tests:
            print("Verifying test '%s'" % test.name)
            try:
                status = self._find_expected_status(test.name, expected)
            except IndexError:
                raise AssertionError("Test '%s' was not expected to be run.%s"
                                     % (test.name, tests_msg))
            expected.pop(expected.index((test.name, status)))
            if status and ':' in status:
                status, message = status.split(':', 1)
            else:
                message = None
            self._check_test_status(test, status, message)
        assert not expected

    def _find_expected_status(self, test, expected):
        for name, status in expected:
            if name == test:
                return status
        raise IndexError

    def should_not_contain_tests(self, suite, *test_names):
        actual_names = [t.name for t in suite.tests]
        for name in test_names:
            if name in actual_names:
                raise AssertionError('Suite should not have contained test "%s"' % name)

    def should_contain_suites(self, suite, *expected):
        print('Suite has suites', suite.suites)
        expected = sorted(expected)
        actual = sorted(s.name for s in suite.suites)
        if len(actual) != len(expected):
            raise AssertionError("Wrong number of suites.\n"
                                 "Expected (%d): %s\n"
                                 "Actual   (%d): %s"
                                 % (len(expected), ', '.join(expected),
                                    len(actual), ', '.join(actual)))
        for name in expected:
            if not utils.Matcher(name).match_any(actual):
                raise AssertionError('Suite %s not found' % name)

    def should_contain_tags(self, test, *tags):
        print('Test has tags', test.tags)
        assert_equal(len(test.tags), len(tags), 'Wrong number of tags')
        tags = sorted(tags, key=lambda s: s.lower().replace('_', '').replace(' ', ''))
        for act, exp in zip(test.tags, tags):
            assert_equal(act, exp)

    def should_contain_keywords(self, item, *kw_names):
        actual_names = [kw.name for kw in item.keywords]
        assert_equal(len(actual_names), len(kw_names), 'Wrong number of keywords')
        for act, exp in zip(actual_names, kw_names):
            assert_equal(act, exp)

    def test_should_have_correct_keywords(self, *kw_names, **config):
        get_var = BuiltIn().get_variable_value
        suite = get_var('${SUITE}')
        name = config.get('name', get_var('${TEST NAME}'))
        kw_index = int(config.get('kw_index', 0))
        test = self._get_test_from_suite(suite, name)
        self._check_test_status(test)
        self.should_contain_keywords(test.keywords[kw_index], *kw_names)
        return test

    def check_log_message(self, item, msg, level='INFO', html=False, pattern=''):
        b = BuiltIn()
        matcher = b.should_match if pattern else b.should_be_equal
        matcher(item.message.rstrip(), msg.rstrip(), 'Wrong log message')
        b.should_be_equal(item.level, 'INFO' if level == 'HTML' else level, 'Wrong log level')
        b.should_be_equal(str(item.html), str(html or level == 'HTML'), 'Wrong HTML status')


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
