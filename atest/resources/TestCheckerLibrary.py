import json
import os
import re
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator
from xmlschema import XMLSchema

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.Collections import Collections
from robot.result import (
    Break, Continue, Error, ExecutionResult, ExecutionResultBuilder, For,
    ForIteration, Group, If, IfBranch, Keyword, Result, ResultVisitor, Return,
    TestCase, TestSuite, Try, TryBranch, Var, While, WhileIteration
)
from robot.result.executionerrors import ExecutionErrors
from robot.result.model import Body, Iterations
from robot.utils.asserts import assert_equal
from robot.utils import eq, get_error_details, is_truthy, Matcher


class WithBodyTraversing:
    body: Body

    def __getitem__(self, index):
        if isinstance(index, str):
            index = tuple(int(i) for i in index.split(','))
        if isinstance(index, (int, slice)):
            return self.body[index]
        if isinstance(index, tuple):
            item = self
            for i in index:
                item = item.body[int(i)]
            return item
        raise TypeError(f"Invalid index {repr(index)}.")

    @property
    def keywords(self):
        return self.body.filter(keywords=True)

    @property
    def messages(self):
        return self.body.filter(messages=True)

    @property
    def non_messages(self):
        return self.body.filter(messages=False)


class ATestKeyword(Keyword, WithBodyTraversing):
    pass


class ATestFor(For, WithBodyTraversing):
    pass


class ATestWhile(While, WithBodyTraversing):
    pass


class ATestGroup(Group, WithBodyTraversing):
    pass


class ATestIf(If, WithBodyTraversing):
    pass


class ATestTry(Try, WithBodyTraversing):
    pass


class ATestVar(Var, WithBodyTraversing):
    pass


class ATestReturn(Return, WithBodyTraversing):
    pass


class ATestBreak(Break, WithBodyTraversing):
    pass


class ATestContinue(Continue, WithBodyTraversing):
    pass


class ATestError(Error, WithBodyTraversing):
    pass


class ATestBody(Body):
    keyword_class = ATestKeyword
    for_class = ATestFor
    if_class = ATestIf
    try_class = ATestTry
    while_class = ATestWhile
    group_class = ATestGroup
    var_class = ATestVar
    return_class = ATestReturn
    break_class = ATestBreak
    continue_class = ATestContinue
    error_class = ATestError


class ATestIfBranch(IfBranch, WithBodyTraversing):
    body_class = ATestBody


class ATestTryBranch(TryBranch, WithBodyTraversing):
    body_class = ATestBody


class ATestForIteration(ForIteration, WithBodyTraversing):
    body_class = ATestBody


class ATestWhileIteration(WhileIteration, WithBodyTraversing):
    body_class = ATestBody


class ATestIterations(Iterations, WithBodyTraversing):
    keyword_class = ATestKeyword


ATestKeyword.body_class = ATestVar.body_class = ATestReturn.body_class \
    = ATestBreak.body_class = ATestContinue.body_class \
    = ATestError.body_class = ATestGroup.body_class \
    = ATestBody
ATestFor.iterations_class = ATestWhile.iterations_class = ATestIterations
ATestFor.iteration_class = ATestForIteration
ATestWhile.iteration_class = ATestWhileIteration
ATestIf.branch_class = ATestIfBranch
ATestTry.branch_class = ATestTryBranch


class ATestTestCase(TestCase, WithBodyTraversing):
    fixture_class = ATestKeyword
    body_class = ATestBody


class ATestTestSuite(TestSuite):
    fixture_class = ATestKeyword
    test_class = ATestTestCase


class TestCheckerLibrary:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.xml_schema = XMLSchema('doc/schema/result.xsd')
        with open('doc/schema/result.json', encoding='UTF-8') as f:
            self.json_schema = Draft202012Validator(json.load(f))

    def process_output(self, path: 'None|Path', validate: 'bool|None' = None):
        set_suite_variable = BuiltIn().set_suite_variable
        if path is None:
            set_suite_variable('$SUITE', None)
            logger.info("Not processing output.")
            return
        if validate is None:
            validate = is_truthy(os.getenv('ATEST_VALIDATE_OUTPUT', False))
        if validate:
            if path.suffix.lower() == '.json':
                self.validate_json_output(path)
            else:
                self._validate_output(path)
        try:
            logger.info(f"Processing output '{path}'.")
            if path.suffix.lower() == '.json':
                result = self._build_result_from_json(path)
            else:
                result = self._build_result_from_xml(path)
        except:
            set_suite_variable('$SUITE', None)
            msg, details = get_error_details()
            logger.info(details)
            raise RuntimeError(f'Processing output failed: {msg}')
        result.visit(ProcessResults())
        set_suite_variable('$SUITE', result.suite)
        set_suite_variable('$STATISTICS', result.statistics)
        set_suite_variable('$ERRORS', result.errors)

    def _build_result_from_xml(self, path):
        result = Result(source=path, suite=ATestTestSuite())
        ExecutionResultBuilder(path).build(result)
        return result

    def _build_result_from_json(self, path):
        with open(path, encoding='UTF-8') as file:
            data = json.load(file)
        return Result(source=path,
                      suite=ATestTestSuite.from_dict(data['suite']),
                      errors=ExecutionErrors(data.get('errors')),
                      rpa=data.get('rpa'),
                      generator=data.get('generator'),
                      generation_time=datetime.fromisoformat(data['generated']))

    def _validate_output(self, path):
        version = self._get_schema_version(path)
        if not version:
            raise ValueError('Schema version not found from XML output.')
        if version != self.xml_schema.version:
            raise ValueError(f'Incompatible schema versions. '
                             f'Schema has `version="{self.xml_schema.version}"` but '
                             f'output file has `schemaversion="{version}"`.')
        self.xml_schema.validate(path)

    def _get_schema_version(self, path):
        with open(path, encoding='UTF-8') as file:
            for line in file:
                if line.startswith('<robot'):
                    return re.search(r'schemaversion="(\d+)"', line).group(1)

    def validate_json_output(self, path: Path):
        with path.open(encoding='UTF') as file:
            self.json_schema.validate(json.load(file))

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
                 if name is None or eq(test.name, name)]
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
        suites = [suite] if eq(suite.name, name) else []
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
            matcher = Matcher(pattern, caseless=False, spaceless=False)
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
            if not Matcher(name).match_any(actual):
                raise AssertionError(f'Suite {name} not found.')

    def should_contain_tags(self, test, *tags):
        logger.info('Test has tags', test.tags)
        assert_equal(len(test.tags), len(tags), 'Wrong number of tags')
        tags = sorted(tags, key=lambda s: s.lower().replace('_', '').replace(' ', ''))
        for act, exp in zip(test.tags, tags):
            assert_equal(act, exp)

    def should_contain_keywords(self, item, *kw_names):
        actual_names = [kw.full_name for kw in item.keywords]
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

    def outputs_should_contain_same_data(self, output1, output2, ignore_timestamps=False):
        dictionaries_should_be_equal = Collections().dictionaries_should_be_equal
        if ignore_timestamps:
            ignore_keys = ['start_time', 'end_time', 'elapsed_time', 'timestamp']
        else:
            ignore_keys = None
        result1 = ExecutionResult(output1)
        result2 = ExecutionResult(output2)
        dictionaries_should_be_equal(result1.suite.to_dict(),
                                     result2.suite.to_dict(),
                                     ignore_keys=ignore_keys)
        dictionaries_should_be_equal(result1.statistics.to_dict(),
                                     result2.statistics.to_dict(),
                                     ignore_keys=ignore_keys)
        # Use `zip(..., strict=True)` when Python 3.10 is minimum version.
        assert len(result1.errors) == len(result2.errors)
        for msg1, msg2 in zip(result1.errors, result2.errors):
            dictionaries_should_be_equal(msg1.to_dict(),
                                         msg2.to_dict(),
                                         ignore_keys=ignore_keys)


class ProcessResults(ResultVisitor):

    def visit_test(self, test):
        for status in 'FAIL', 'SKIP', 'PASS':
            if status in test.doc:
                test.exp_status = status
                test.exp_message = test.doc.split(status, 1)[1].lstrip()
                break
        else:
            test.exp_status = 'PASS'
            test.exp_message = ''
