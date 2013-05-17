from robot.parsing import TestData

from .model import TestSuite


class TestSuiteBuilder(object):

    def __init__(self):
        pass

    def build(self, path):
        return self._build(TestData(source=path))

    def _build(self, data):
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=data.setting_table.doc.value)
        for imp in data.setting_table.imports:
            suite.imports.create(type=imp.type,
                                 name=imp.name,
                                 args=tuple(imp.args),
                                 alias=imp.alias)
        for var_data in data.variable_table.variables:
            if var_data.name.startswith('$'):
                value = var_data.value[0]
            else:
                value = var_data.value
            suite.variables.create(name=var_data.name,
                                   value=value)
        for uk_data in data.keyword_table.keywords:
            uk = suite.user_keywords.create(name=uk_data.name,
                                            args=tuple(uk_data.args))
            for kw_data in uk_data.steps:
                uk.keywords.create(name=kw_data.keyword,
                                   args=tuple(kw_data.args),
                                   assign=tuple(kw_data.assign))
        for test_data in data.testcase_table.tests:
            test = suite.tests.create(name=test_data.name,
                                      doc=test_data.doc.value,
                                      tags=self._get_tags(test_data,
                                                          data.setting_table))
            for kw_data in test_data.steps:
                test.keywords.create(name=kw_data.keyword,
                                     args=tuple(kw_data.args),
                                     assign=tuple(kw_data.assign))
        for child in data.children:
            suite.suites.append(self._build(child))
        return suite

    def _get_tags(self, test, settings):
        tags = test.tags.value
        defaults = settings.default_tags.value or []
        forced = settings.force_tags.value or []
        if tags is None:
            tags = defaults
        return tags + forced
