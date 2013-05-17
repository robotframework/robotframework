from robot.parsing import TestData

from .model import TestSuite


class TestSuiteBuilder(object):

    def __init__(self):
        pass

    def build(self, *paths):
        if len(paths) == 1:
            return self._build(TestData(source=paths[0]))
        root = TestSuite()
        for path in paths:
            root.suites.append(self._build(TestData(source=path)))
        return root

    def _build(self, data):
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=data.setting_table.doc.value)
        for imp in data.setting_table.imports:
            suite.imports.create(type=imp.type,
                                 name=imp.name,
                                 args=tuple(imp.args),
                                 alias=imp.alias)
        suite_setup = data.setting_table.suite_setup
        if suite_setup:
            suite.keywords.create(type='setup',
                                  name=suite_setup.name,
                                  args=tuple(suite_setup.args))
        suite_teardown = data.setting_table.suite_teardown
        if suite_teardown:
            suite.keywords.create(type='teardown',
                                  name=suite_teardown.name,
                                  args=tuple(suite_teardown.args))
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
            test_setup = test_data.setup or test_data.parent.parent.setting_table.test_setup
            if test_setup:
                test.keywords.create(type='setup',
                                     name=test_setup.name,
                                     args=tuple(test_setup.args))
            for kw_data in test_data.steps:
                test.keywords.create(name=kw_data.keyword,
                                     args=tuple(kw_data.args),
                                     assign=tuple(kw_data.assign))
            test_teardown = test_data.teardown or test_data.parent.parent.setting_table.test_teardown
            if test_teardown:
                test.keywords.create(type='teardown',
                                     name=test_teardown.name,
                                     args=tuple(test_teardown.args))
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
