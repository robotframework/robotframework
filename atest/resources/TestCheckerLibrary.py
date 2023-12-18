import os
import re

from xmlschema import XMLSchema

from robot import utils
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.result import (Break, Continue, Error, ExecutionResultBuilder, For,
                          ForIteration, If, IfBranch, Keyword, Result, ResultVisitor,
                          Return, TestCase, TestSuite, Try, TryBranch, Var, While,
                          WhileIteration)
from robot.result.model import Body, Iterations
from robot.utils.asserts import assert_equal


class NoSlotsKeyword(Keyword):
    pass


class NoSlotsFor(For):
    pass


class NoSlotsWhile(While):
    pass


class NoSlotsIf(If):
    pass


class NoSlotsTry(Try):
    pass


class NoSlotsVar(Var):
    pass


class NoSlotsReturn(Return):
    pass


class NoSlotsBreak(Break):
    pass


class NoSlotsContinue(Continue):
    pass


class NoSlotsError(Error):
    pass


class NoSlotsBody(Body):
    keyword_class = NoSlotsKeyword
    for_class = NoSlotsFor
    if_class = NoSlotsIf
    try_class = NoSlotsTry
    while_class = NoSlotsWhile
    var_class = NoSlotsVar
    return_class = NoSlotsReturn
    break_class = NoSlotsBreak
    continue_class = NoSlotsContinue
    error_class = NoSlotsError


class NoSlotsIfBranch(IfBranch):
    body_class = NoSlotsBody


class NoSlotsTryBranch(TryBranch):
    body_class = NoSlotsBody


class NoSlotsForIteration(ForIteration):
    body_class = NoSlotsBody


class NoSlotsWhileIteration(WhileIteration):
    body_class = NoSlotsBody


class NoSlotsIterations(Iterations):
    keyword_class = NoSlotsKeyword


NoSlotsKeyword.body_class = NoSlotsVar.body_class = NoSlotsReturn.body_class \
    = NoSlotsBreak.body_class = NoSlotsContinue.body_class \
    = NoSlotsError.body_class = NoSlotsBody
NoSlotsFor.iterations_class = NoSlotsWhile.iterations_class = NoSlotsIterations
NoSlotsFor.iteration_class = NoSlotsForIteration
NoSlotsWhile.iteration_class = NoSlotsWhileIteration
NoSlotsIf.branch_class = NoSlotsIfBranch
NoSlotsTry.branch_class = NoSlotsTryBranch


class NoSlotsTestCase(TestCase):
    fixture_class = NoSlotsKeyword
    body_class = NoSlotsBody


class NoSlotsTestSuite(TestSuite):
    fixture_class = NoSlotsKeyword
    test_class = NoSlotsTestCase


class TestCheckerLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.schema = XMLSchema('doc/schema/robot.xsd')

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
                    return re.search(r'schemaversion="(\d+)"', line).group(1)

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
                    msg = f"Error message:\n{test.message}"
                else:
                    msg = f"Test message:\n{test.message}"
            else:
                msg = f"Expected message:\n{test.exp_message}"
            raise AssertionError(
                f"Status of '{test.name}' should have been {test.exp_status} "
                f"but it was {test.status}.\n\n{msg}"
            )
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
        raise AssertionError(f"Test '{test.name}' had wrong message.\n\n"
                             f"Expected:\n{test.exp_message}\n\n"
                             f"Actual:\n{test.message}\n")

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
            logger.info(f"Verifying test '{test.name}'")
            try:
                status = self._find_expected_status(test.name, expected)
            except IndexError:
                raise AssertionError(f"Test '{test.name}' was not expected to be run."
                                     + tests_msg)
            expected.pop(expected.index((test.name, status)))
            if status and ':' in status:
                status, message = status.split(':', 1)
            elif status:
                message = ''
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
            raise AssertionError(f"Wrong number of suites.\n"
                                 f"Expected ({len(expected)}): {', '.join(expected)}\n"
                                 f"Actual   ({len(actual)}): {', '.join(actual)}")
        for name in expected:
            if not utils.Matcher(name).match_any(actual):
                raise AssertionError(f'Suite {name} not found.')

    def should_contain_tags(self, test, *tags):
        logger.info('Test has tags', test.tags)
        assert_equal(len(test.tags), len(tags), 'Wrong number of tags')
        tags = sorted(tags, key=lambda s: s.lower().replace('_', '').replace(' ', ''))
        for act, exp in zip(test.tags, tags):
            assert_equal(act, exp)

    def should_contain_keywords(self, item, *kw_names):
        actual_names = [kw.full_name for kw in item.kws]
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

    def check_log_message(self, item, expected, level='INFO', html=False, pattern=False, traceback=False):
        message = item.message.rstrip()
        if traceback:
            # Remove `^^^` lines added by Python 3.11+.
            message = '\n'.join(line for line in message.splitlines()
                                if '^' not in line or line.strip('^ '))
        b = BuiltIn()
        matcher = b.should_match if pattern else b.should_be_equal
        matcher(message, expected.rstrip(), 'Wrong log message')
        if level != 'IGNORE':
            b.should_be_equal(item.level, 'INFO' if level == 'HTML' else level, 'Wrong log level')
        b.should_be_equal(str(item.html), str(html or level == 'HTML'), 'Wrong HTML status')

    def outputs_should_be_equal(self, output1, output2):
        suite1 = self._parse_output(output1)
        suite2 = self._parse_output(output2)
        assert suite1.to_dict() == suite2.to_dict()

    def _parse_output(self, output) -> TestSuite:
        from_source = {'xml': TestSuite.from_xml,
                       'json': TestSuite.from_json}[output.rsplit('.')[-1].lower()]
        return from_source(output)


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

    def start_body_item(self, item):
        # TODO: Consider not setting these attributes to avoid "NoSlots" variants.
        # - Using normal `body` and `messages` would in general be cleaner.
        # - If `kws` is preserved, it should only contain keywords, not controls.
        # - `msgs` isn't that much shorter than `messages`.
        item.kws = item.body.filter(messages=False)
        item.msgs = item.body.filter(messages=True)

    def visit_message(self, message):
        pass

    def visit_errors(self, errors):
        errors.msgs = errors.messages
