import unittest
from pathlib import Path

from robot.errors import DataError
from robot.utils import Importer
from robot.utils.asserts import assert_equal, assert_raises, assert_true
from robot.running import TestSuite, TestSuiteBuilder


DATADIR = (Path(__file__).parent / '../../atest/testdata/misc').resolve()


def build(*paths, **config):
    paths = [Path(DATADIR, p).resolve() for p in paths]
    suite = TestSuiteBuilder(**config).build(*paths)
    assert_true(isinstance(suite, TestSuite))
    assert_equal(suite.source, paths[0] if len(paths) == 1 else None)
    return suite


def assert_keyword(kw, assign=(), name='', args=(), type='KEYWORD'):
    assert_equal(kw.name, name)
    assert_equal(kw.args, args)
    assert_equal(kw.assign, assign)
    assert_equal(kw.type, type)


class TestBuilding(unittest.TestCase):

    def test_suite_data(self):
        suite = build('pass_and_fail.robot')
        assert_equal(suite.name, 'Pass And Fail')
        assert_equal(suite.doc, 'Some tests here')
        assert_equal(suite.metadata, {})

    def test_imports(self):
        imp = build('dummy_lib_test.robot').resource.imports[0]
        assert_equal(imp.type, 'LIBRARY')
        assert_equal(imp.name, 'DummyLib')
        assert_equal(imp.args, ())

    def test_variables(self):
        variables = build('pass_and_fail.robot').resource.variables
        assert_equal(variables[0].name, '${LEVEL1}')
        assert_equal(variables[0].value, ('INFO',))
        assert_equal(variables[1].name, '${LEVEL2}')
        assert_equal(variables[1].value, ('DEBUG',))

    def test_user_keywords(self):
        uk = build('pass_and_fail.robot').resource.keywords[0]
        assert_equal(uk.name, 'My Keyword')
        assert_equal([str(a) for a in uk.args], ['who'])

    def test_test_data(self):
        test = build('pass_and_fail.robot').tests[1]
        assert_equal(test.name, 'Fail')
        assert_equal(test.doc, 'FAIL Expected failure')
        assert_equal(list(test.tags), ['fail', 'force'])
        assert_equal(test.timeout, None)
        assert_equal(test.template, None)

    def test_test_keywords(self):
        kw = build('pass_and_fail.robot').tests[0].body[0]
        assert_keyword(kw, (), 'My Keyword', ('Pass',))

    def test_assign(self):
        kw = build('non_ascii.robot').tests[1].body[0]
        assert_keyword(kw, ('${msg} =',), 'Evaluate', (r"u'Fran\\xe7ais'",))

    def test_directory_suite(self):
        suite = build('suites')
        assert_equal(suite.name, 'Suites')
        assert_equal(suite.suites[0].name, 'Suite With Prefix')
        assert_equal(suite.suites[2].name, 'Subsuites')
        assert_equal(suite.suites[4].name, 'Suite With Double Underscore')
        assert_equal(suite.suites[4].suites[0].name, 'Tests With Double Underscore')
        assert_equal(suite.suites[-1].name, 'Tsuite3')
        assert_equal(suite.suites[2].suites[1].name, 'Sub2')
        assert_equal(len(suite.suites[2].suites[1].tests), 1)
        assert_equal(suite.suites[2].suites[1].tests[0].id, 's1-s3-s2-t1')

    def test_multiple_inputs(self):
        suite = build('pass_and_fail.robot', 'normal.robot')
        assert_equal(suite.name, 'Pass And Fail & Normal')
        assert_equal(suite.suites[0].name, 'Pass And Fail')
        assert_equal(suite.suites[1].name, 'Normal')
        assert_equal(suite.suites[1].tests[1].id, 's1-s2-t2')

    def test_suite_setup_and_teardown(self):
        suite = build('setups_and_teardowns.robot')
        assert_keyword(suite.setup, name='${SUITE SETUP}', type='SETUP')
        assert_keyword(suite.teardown, name='${SUITE TEARDOWN}', type='TEARDOWN')

    def test_test_setup_and_teardown(self):
        test = build('setups_and_teardowns.robot').tests[0]
        assert_keyword(test.setup, name='${TEST SETUP}', type='SETUP')
        assert_keyword(test.teardown, name='${TEST TEARDOWN}', type='TEARDOWN')
        assert_equal([kw.name for kw in test.body], ['Keyword'])

    def test_test_timeout(self):
        tests = build('timeouts.robot').tests
        assert_equal(tests[0].timeout, '1min 42s')
        assert_equal(tests[1].timeout, '${100}')
        assert_equal(tests[2].timeout, None)

    def test_keyword_timeout(self):
        kw = build('timeouts.robot').resource.keywords[0]
        assert_equal(kw.timeout, '42')

    def test_rpa(self):
        for paths in [('.',), ('pass_and_fail.robot',),
                      ('pass_and_fail.robot', 'normal.robot')]:
            self._validate_rpa(build(*paths), False)
            self._validate_rpa(build(*paths, rpa=True), True)
        self._validate_rpa(build('../rpa/tasks1.robot'), True)
        self._validate_rpa(build('../rpa/', rpa=False), False)
        suite = build('../rpa/')
        assert_equal(suite.rpa, None)
        for child in suite.suites:
            self._validate_rpa(child, child.name != 'Tests')

    def _validate_rpa(self, suite, expected):
        assert_equal(suite.rpa, expected, suite.name)
        for child in suite.suites:
            self._validate_rpa(child, expected)

    def test_custom_parser(self):
        path = DATADIR / '../parsing/custom/CustomParser.py'
        for parser in [path, str(path)]:
            suite = build('../parsing/custom/tests.custom', custom_parsers=[parser])
            assert_equal(suite.name, 'Tests')
            assert_equal([t.name for t in suite.tests], ['Passing', 'Failing', 'Empty'])

    def test_custom_parser_with_args(self):
        path = DATADIR / '../parsing/custom/CustomParser.py:custom'
        for parser in [path, str(path)]:
            suite = build('../parsing/custom/tests.custom', custom_parsers=[parser])
            assert_equal(suite.name, 'Tests')
            assert_equal([t.name for t in suite.tests], ['Passing', 'Failing', 'Empty'])

    def test_custom_parser_as_object(self):
        path = DATADIR / '../parsing/custom/CustomParser.py'
        parser = Importer().import_class_or_module(path, instantiate_with_args=())
        suite = build('../parsing/custom/tests.custom', custom_parsers=[parser])
        assert_equal(suite.name, 'Tests')
        assert_equal([t.name for t in suite.tests], ['Passing', 'Failing', 'Empty'])

    def test_failing_parser_import(self):
        err = assert_raises(DataError, build, custom_parsers=['non_existing_mod'])
        assert_true(err.message.startswith("Importing parser 'non_existing_mod' failed:"))

    def test_incompatible_parser_object(self):
        err = assert_raises(DataError, build, custom_parsers=[42])
        assert_equal(err.message, "Importing parser 'integer' failed: "
                                  "'integer' does not have mandatory 'parse' method.")


class TestTemplates(unittest.TestCase):

    def test_from_setting_table(self):
        test = build('../running/test_template.robot').tests[0]
        assert_keyword(test.body[0], (), 'Should Be Equal', ('Fail', 'Fail'))
        assert_equal(test.template, 'Should Be Equal')

    def test_from_test_case(self):
        test = build('../running/test_template.robot').tests[3]
        kws = test.body
        assert_keyword(kws[0], (), 'Should Not Be Equal', ('Same', 'Same'))
        assert_keyword(kws[1], (), 'Should Not Be Equal', ('42', '43'))
        assert_keyword(kws[2], (), 'Should Not Be Equal', ('Something', 'Different'))
        assert_equal(test.template, 'Should Not Be Equal')

    def test_no_variable_assign(self):
        test = build('../running/test_template.robot').tests[8]
        assert_keyword(test.body[0], (), 'Expect Exactly Three Args',
                       ('${SAME VARIABLE}', 'Variable content', '${VARIABLE}'))
        assert_equal(test.template, 'Expect Exactly Three Args')


if __name__ == '__main__':
    unittest.main()
