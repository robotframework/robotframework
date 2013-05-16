from robot.parsing import TestData

from .model import TestSuite


class TestSuiteBuilder(object):

    def __init__(self):
        pass

    def build(self, path):
        data = TestData(source=path)
        suite = TestSuite(name=data.name,
                          source=data.source,
                          doc=data.setting_table.doc.value)
        for imp in data.setting_table.imports:
            suite.imports.create(type=imp.type,
                                 name=imp.name,
                                 args=tuple(imp.args),
                                 alias=imp.alias)
        for test_data in data.testcase_table.tests:
            test = suite.tests.create(name=test_data.name,
                                      doc=test_data.doc.value,
                                      tags=self._get_tags(test_data,
                                                          data.setting_table))
            for kw_data in test_data.steps:
                test.keywords.create(name=kw_data.keyword,
                                     args=tuple(kw_data.args),
                                     assign=tuple(kw_data.assign))
        return suite

    def _get_tags(self, test, settings):
        tags = test.tags.value
        defaults = settings.default_tags.value or []
        forced = settings.force_tags.value or []
        if tags is None:
            tags = defaults
        return tags + forced
