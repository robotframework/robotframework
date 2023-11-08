import unittest

from robot.utils.asserts import assert_true, assert_equal
from test_jsmodelbuilders import remap
from robot.reporting.jsexecutionresult import (JsExecutionResult,
                                               _KeywordRemover, StringIndex)
from robot.reporting.jsmodelbuilders import SuiteBuilder, JsBuildingContext
from robot.result import TestSuite


class TestRemoveDataNotNeededInReport(unittest.TestCase):

    def test_remove_keywords(self):
        model = self._create_suite_model()
        expected = self._get_expected_suite_model(model)
        result = _KeywordRemover().remove_keywords(model)
        assert_equal(result, expected)
        self._verify_model_contains_no_keywords(result)

    def _create_suite_model(self):
        self.context = JsBuildingContext()
        return SuiteBuilder(self.context).build(self._get_suite())

    def _get_suite(self):
        suite = TestSuite(name='root', doc='sdoc', metadata={'m': 'v'})
        suite.setup.config(name='keyword')
        sub = suite.suites.create(name='suite', metadata={'a': '1', 'b': '2'})
        sub.setup.config(name='keyword')
        t1 = sub.tests.create(name='test', tags=['t1'])
        t1.body.create_keyword(name='keyword')
        t1.body.create_keyword(name='keyword')
        t2 = sub.tests.create(name='test', tags=['t1', 't2'])
        t2.body.create_keyword(name='keyword')
        return suite

    def _get_expected_suite_model(self, suite):
        suite = list(suite)
        suite[-4] = tuple(self._get_expected_suite_model(s) for s in suite[-4])
        suite[-3] = tuple(self._get_expected_test_model(t) for t in suite[-3])
        suite[-2] = ()
        return tuple(suite)

    def _get_expected_test_model(self, test):
        test = list(test)
        test[-1] = ()
        return tuple(test)

    def _verify_model_contains_no_keywords(self, model, mapped=False):
        if not mapped:
            model = remap(model, self.context.strings)
        assert_true('keyword' not in model, 'Not all keywords removed')
        for item in model:
            if isinstance(item, tuple):
                self._verify_model_contains_no_keywords(item, mapped=True)

    def test_remove_unused_strings(self):
        strings = ('', 'hei', 'hoi')
        model = (1, StringIndex(0), 42, StringIndex(2), -1, None)
        model, strings = _KeywordRemover().remove_unused_strings(model, strings)
        assert_equal(strings, ('', 'hoi'))
        assert_equal(model, (1, 0, 42, 1, -1, None))

    def test_remove_unused_strings_nested(self):
        strings = tuple(' abcde')
        model = (StringIndex(0), StringIndex(1), 2, 3, StringIndex(4), 5,
                 (0, StringIndex(1), 2, StringIndex(3), 4, 5))
        model, strings = _KeywordRemover().remove_unused_strings(model, strings)
        assert_equal(strings, tuple(' acd'))
        assert_equal(model, (0, 1, 2, 3, 3, 5, (0, 1, 2, 2, 4, 5)))

    def test_through_jsexecutionresult(self):
        suite = (0, StringIndex(1), 2, 3, 4, StringIndex(5),
                 ((0, 1, 2, StringIndex(3), 4, 5, (), (), ('suite', 'kws'), 9),),
                 ((0, 1, 2, StringIndex(3), 4, 5, ('test', 'kws')),
                  (0, StringIndex(1), 2, 3, 4, 5, ('test', 'kws'))),
                 ('suite', 'kws'), 9)
        exp_s = (0, 0, 2, 3, 4, 2,
                 ((0, 1, 2, 1, 4, 5, (), (), (), 9),),
                 ((0, 1, 2, 1, 4, 5, ()),
                  (0, 0, 2, 3, 4, 5, ())),
                 (), 9)
        result = JsExecutionResult(suite=suite, strings=tuple(' ABCDEF'),
                                   errors=(1, 2), statistics={}, basemillis=0,
                                   min_level='DEBUG')
        assert_equal(result.data['errors'], (1, 2))
        result.remove_data_not_needed_in_report()
        assert_equal(result.strings, tuple('ACE'))
        assert_equal(result.suite, exp_s)
        assert_equal(result.min_level, 'DEBUG')
        assert_true('errors' not in result.data)


if __name__ == '__main__':
    unittest.main()
