import os
import re

from xmlschema import XMLSchema

from robot import utils
from robot.api import logger
from robot.utils.asserts import assert_equal
from robot.result import (ExecutionResultBuilder, For, If, ForIteration, Keyword,
                          Result, ResultVisitor, TestCase, TestSuite)
from robot.result.model import Body, ForIterations, IfBranches, IfBranch
from robot.libraries.BuiltIn import BuiltIn


class NoSlotsKeyword(Keyword):
    pass


class NoSlotsFor(For):
    pass


class NoSlotsIf(If):
    pass


class NoSlotsBody(Body):
    keyword_class = NoSlotsKeyword
    for_class = NoSlotsFor
    if_class = NoSlotsIf


class NoSlotsIfBranch(IfBranch):
    body_class = NoSlotsBody


class NoSlotsIfBranches(IfBranches):
    if_branch_class = NoSlotsIfBranch


class NoSlotsForIteration(ForIteration):
    body_class = NoSlotsBody


class NoSlotsForIterations(ForIterations):
    for_iteration_class = NoSlotsForIteration
    keyword_class = NoSlotsKeyword


NoSlotsKeyword.body_class = NoSlotsBody
NoSlotsFor.body_class = NoSlotsForIterations
NoSlotsIf.body_class = NoSlotsIfBranches


class NoSlotsTestCase(TestCase):
    fixture_class = NoSlotsKeyword
    body_class = NoSlotsBody


class NoSlotsTestSuite(TestSuite):
    fixture_class = NoSlotsKeyword
    test_class = NoSlotsTestCase


class TestCheckerLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.schema = XMLSchema('doc/schema/robot.02.xsd')

    def process_output(self, path, validate=None):
        set_suite_variable = BuiltIn().set_suite_variable
        if not path or path.upper() == 'NONE':
            set_suite_variable('$SUITE', None)
            logger.info("Not processing output.")
            return
        path = path.replace('/', os.sep)
        if validate is None:
            validate = os.getenv('ATEST_VALIDATE_OUTPUT', False)
        if utils.is_truthy(validate):
            self._validate_output(path)
        try:
            logger.info("Processing output '%s'." % path)
            result = Result(root_suite=NoSlotsTestSuite())
            ExecutionResultBuilder(path).build(result)
        except:
            set_suite_variable('$SUITE', None)
            msg, details = utils.get_error_details()
            logger.info(details)
            raise RuntimeError('Processing output failed: %s' % msg)
        result.visit(ProcessResults())
        set_suite_variable('$SUITE', result.suite)
        set_suite_variable('$STATISTICS', result.statistics)
        set_suite_variable('$ERRORS', result.errors)

    def _validate_output(self, path):
        schema_version = self._get_schema_version(path)
        if schema_version != self.schema.version:
            raise AssertionError(
                'Incompatible schema versions. Schema has `version="%s"` '
                'but output file has `schemaversion="%s"`.'
                % (self.schema.version, schema_version)
        )
        self.schema.validate(path)

    def _get_schema_version(self, path):
        with open(path, encoding='UTF-8') as f:
            for line in f:
                if line.startswith('<robot'):
                    return re.search('schemaversion="(\d+)"', line).group(1)

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
                if test.status == 'FAIL':
                    msg = ("Test '%s' was expected to PASS but it FAILED.\n\n"
                           "Error message:\n%s" % (test.name, test.message))
                else:
                    msg = ("Test '%s' was expected to PASS but it was SKIPPED.\n\n"
                           "Test message:\n%s" % (test.name, test.message))
            else:
                msg = ("Test '%s' was expected to %s but it %sED.\n\n"
                       "Expected message:\n%s" % (test.name, test.exp_status,
                                                  test.status, test.exp_message))
            raise AssertionError(msg)
        if test.exp_message == test.message:
            return
        if test.exp_message.startswith('REGEXP:'):
            pattern = self._get_pattern(test, 'REGEXP:')
            if re.match('^%s$' % pattern, test.message, re.DOTALL):
                return
        if test.exp_message.startswith('GLOB:'):
            pattern = self._get_pattern(test, 'GLOB:')
            matcher = utils.Matcher(pattern, caseless=False, spaceless=False)
            if matcher.match(test.message):
                return
        if test.exp_message.startswith('STARTS:'):
            start = self._get_pattern(test, 'STARTS:')
            if test.message.startswith(start):
                return
        raise AssertionError("Test '%s' had wrong message.\n\n"
                             "Expected:\n%s\n\nActual:\n%s\n"
                             % (test.name, test.exp_message, test.message))

    def _get_pattern(self, test, prefix):
        pattern = test.exp_message[len(prefix):].strip()
        if not pattern:
            raise RuntimeError("Empty '%s' is not allowed!")
        return pattern

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
            logger.info("Verifying test '%s'" % test.name)
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
        logger.info('Suite has suites', suite.suites)
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
        logger.info('Test has tags', test.tags)
        assert_equal(len(test.tags), len(tags), 'Wrong number of tags')
        tags = sorted(tags, key=lambda s: s.lower().replace('_', '').replace(' ', ''))
        for act, exp in zip(test.tags, tags):
            assert_equal(act, exp)

    def should_contain_keywords(self, item, *kw_names):
        actual_names = [kw.name for kw in item.kws]
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
        self.should_contain_keywords(test.body[kw_index], *kw_names)
        return test

    def check_log_message(self, item, msg, level='INFO', html=False, pattern=False):
        b = BuiltIn()
        matcher = b.should_match if pattern else b.should_be_equal
        matcher(item.message.rstrip(), msg.rstrip(), 'Wrong log message')
        b.should_be_equal(item.level, 'INFO' if level == 'HTML' else level, 'Wrong log level')
        b.should_be_equal(str(item.html), str(html or level == 'HTML'), 'Wrong HTML status')


class ProcessResults(ResultVisitor):

    def start_test(self, test):
        for status in 'FAIL', 'SKIP', 'PASS':
            if status in test.doc:
                test.exp_status = status
                test.exp_message = test.doc.split(status, 1)[1].lstrip()
                break
        else:
            test.exp_status = 'PASS'
            test.exp_message = ''
        test.kws = list(test.body)
        test.keyword_count = test.kw_count = len(test.kws)

    def start_keyword(self, kw):
        self._add_kws_and_msgs(kw)

    def _add_kws_and_msgs(self, item):
        item.kws = item.body.filter(messages=False)
        item.msgs = item.body.filter(messages=True)
        item.keyword_count = item.kw_count = len(item.kws)
        item.message_count = item.msg_count = len(item.msgs)

    def start_for(self, for_):
        self._add_kws_and_msgs(for_)

    def start_for_iteration(self, iteration):
        self._add_kws_and_msgs(iteration)

    def start_if(self, if_):
        self._add_kws_and_msgs(if_)

    def start_if_branch(self, branch):
        self._add_kws_and_msgs(branch)

    def start_try(self, try_):
        self._add_kws_and_msgs(try_)

    def visit_errors(self, errors):
        errors.msgs = errors.messages
        errors.message_count = errors.msg_count = len(errors.messages)
