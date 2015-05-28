import unittest
from os.path import abspath, dirname, normpath, join

from robot.utils.asserts import assert_equals, assert_true
from robot.running import TestSuite, TestSuiteBuilder


CURDIR = dirname(abspath(__file__))
DATADIR = join(CURDIR, '..', '..', 'atest', 'testdata', 'misc')


def build(*paths):
    paths = [normpath(join(DATADIR, p)) for p in paths]
    suite = TestSuiteBuilder().build(*paths)
    assert_true(isinstance(suite, TestSuite))
    assert_equals(suite.source, paths[0] if len(paths) == 1 else None)
    return suite


def assert_keyword(kw, assign=(), name='', args=(), type='kw'):
    assert_equals(kw.name, name)
    assert_equals(kw.args, args)
    assert_equals(kw.assign, assign)
    assert_equals(kw.type, type)


class TestBuilding(unittest.TestCase):

    def test_suite_data(self):
        suite = build('pass_and_fail.robot')
        assert_equals(suite.name, 'Pass And Fail')
        assert_equals(suite.doc, 'Some tests here')
        assert_equals(suite.metadata, {})

    def test_imports(self):
        imp = build('dummy_lib_test.robot').resource.imports[0]
        assert_equals(imp.type, 'Library')
        assert_equals(imp.name, 'DummyLib')
        assert_equals(imp.args, ())

    def test_variables(self):
        variables = build('pass_and_fail.robot').resource.variables
        assert_equals(variables[0].name, '${LEVEL1}')
        assert_equals(variables[0].value, ['INFO'])
        assert_equals(variables[1].name, '${LEVEL2}')
        assert_equals(variables[1].value, ['DEBUG'])

    def test_user_keywords(self):
        uk = build('pass_and_fail.robot').resource.keywords[0]
        assert_equals(uk.name, 'My Keyword')
        assert_equals(uk.args, ('${who}',))

    def test_test_data(self):
        test = build('pass_and_fail.robot').tests[1]
        assert_equals(test.name, 'Fail')
        assert_equals(test.doc, 'FAIL Expected failure')
        assert_equals(list(test.tags), ['fail', 'force'])
        assert_equals(test.timeout, None)
        assert_equals(test.template, None)

    def test_test_keywords(self):
        kw = build('pass_and_fail.robot').tests[0].keywords[0]
        assert_keyword(kw, (), 'My Keyword', ('Pass',))

    def test_assign(self):
        kw = build('unicode.robot').tests[1].keywords[0]
        assert_keyword(kw, ('${msg} =',), 'Evaluate', (r"u'Fran\\xe7ais'",))

    def test_directory_suite(self):
        suite = build('suites')
        assert_equals(suite.name, 'Suites')
        assert_equals(suite.suites[1].name, 'Subsuites')
        assert_equals(suite.suites[-1].name, 'Tsuite3')
        assert_equals(suite.suites[1].suites[1].name, 'Sub2')
        assert_equals(len(suite.suites[1].suites[1].tests), 1)
        assert_equals(suite.suites[1].suites[1].tests[0].id, 's1-s2-s2-t1')

    def test_multiple_inputs(self):
        suite = build('pass_and_fail.robot', 'normal.robot')
        assert_equals(suite.name, 'Pass And Fail & Normal')
        assert_equals(suite.suites[0].name, 'Pass And Fail')
        assert_equals(suite.suites[1].name, 'Normal')
        assert_equals(suite.suites[1].tests[1].id, 's1-s2-t2')

    def test_suite_setup_and_teardown(self):
        kws = build('setups_and_teardowns.robot').keywords
        assert_keyword(kws.setup, name='${SUITE SETUP}', type='setup')
        assert_keyword(kws.teardown, name='${SUITE TEARDOWN}', type='teardown')

    def test_test_setup_and_teardown(self):
        kws = build('setups_and_teardowns.robot').tests[0].keywords
        assert_keyword(kws.setup, name='${TEST SETUP}', type='setup')
        assert_keyword(kws.teardown, name='${TEST TEARDOWN}', type='teardown')
        assert_equals([kw.name for kw in kws],
                      ['${TEST SETUP}', 'Keyword', '${TEST TEARDOWN}'])
        assert_equals([kw.name for kw in kws.normal], ['Keyword'])

    def test_test_timeout(self):
        tests = build('timeouts.robot').tests
        assert_equals(tests[0].timeout.value, '1min 42s')
        assert_equals(tests[0].timeout.message, '')
        assert_equals(tests[1].timeout.value, '1d2h')
        assert_equals(tests[1].timeout.message, 'The message')
        assert_equals(tests[2].timeout.value, '${100}')
        assert_equals(tests[2].timeout.message, '')

    def test_keyword_timeout(self):
        # TODO: Tests and uks have inconsistent timeout types.
        kw = build('timeouts.robot').resource.keywords[0]
        assert_equals(kw.timeout.value, '42')
        assert_equals(kw.timeout.message, 'My message')


class TestTemplates(unittest.TestCase):

    def test_from_setting_table(self):
        test = build('../running/test_template.robot').tests[0]
        assert_keyword(test.keywords[0], (), 'Should Be Equal', ('Fail', 'Fail'))
        assert_equals(test.template, 'Should Be Equal')

    def test_from_test_case(self):
        test = build('../running/test_template.robot').tests[3]
        kws = test.keywords
        assert_keyword(kws[0], (), 'Should Not Be Equal', ('Same', 'Same'))
        assert_keyword(kws[1], (), 'Should Not Be Equal', ('42', '43'))
        assert_keyword(kws[2], (), 'Should Not Be Equal', ('Something', 'Different'))
        assert_equals(test.template, 'Should Not Be Equal')

    def test_no_variable_assign(self):
        test = build('../running/test_template.robot').tests[8]
        assert_keyword(test.keywords[0], (), 'Expect Exactly Three Args',
                       ('${SAME VARIABLE}', 'Variable content', '${VARIABLE}'))
        assert_equals(test.template, 'Expect Exactly Three Args')
