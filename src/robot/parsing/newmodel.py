#  Copyright 2008-2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

class TestCaseFile(object):

    def __init__(self, source=None):
        self.source = source
        self.setting_table = SettingTable()
        self.variable_table = VariableTable()
        self.testcase_table = TestCaseTable()
        self.keyword_table = KeywordTable()

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table

    def edited(self):
        return any(table.edited() for table in self)


class DataTable(object):

    def edited(self):
        return False

class SettingTable(DataTable):

    def __init__(self):
        self.doc = Documentation()
        self.suite_setup = Fixture()
        self.suite_teardown = Fixture()
        self.metadata = Metadata()
        self.test_setup = Fixture()
        self.test_teardown = Fixture()
        self.test_timeout = Timeout()
        self.force_tags = Tags()
        self.default_tags = Tags()
        self.imports = []

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.metadata, self.test_setup, self.test_teardown,
                        self.test_timeout, self.force_tags, self.default_tags] \
                        + self.imports:
            yield setting

    def edited(self):
        return any(setting.edited() for setting in self)

class VariableTable(DataTable):

    def __init__(self):
        self.variables = []

    def add(self, name, value):
        self.variables.append(Variable(name, value))

class TestCaseTable(DataTable):

    def __init__(self):
        self.tests = []

    def add(self, name):
        self.tests.append(TestCase(name))
        return self.tests[-1]

class KeywordTable(DataTable):

    def __init__(self):
        self.keywords = []

    def add(self, name):
        self.keywords.append(UserKeyword(name))
        return self.keywords[-1]


class Setting(object):

    def __init__(self):
        self.value = []

    def set(self, value):
        self.value = value

    def edited(self):
        return bool(self.value)

class Documentation(Setting):

    def __init__(self):
        self.value = ''

    def set(self, value):
        if not isinstance(value, basestring):
            value = ' '.join(value)
        self.value = value

class Fixture(Setting):
    pass

class Metadata(Setting):
    pass

class Timeout(Setting):
    pass

class Tags(Setting):
    pass

class Arguments(Setting):
    pass

class Return(Setting):
    pass


class Variable(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value


class TestCase(object):

    def __init__(self, name):
        self.name = name
        self.doc = Documentation()
        self.tags = Tags()
        self.setup = Fixture()
        self.teardown = Fixture()
        self.timeout = Timeout()
        self.steps = []

    def add_step(self, content):
        self.steps.append(Step(content))


class UserKeyword(object):

    def __init__(self, name):
        self.name = name
        self.doc = Documentation()
        self.args = Arguments()
        self.return_ = Return()
        self.timeout = Timeout()
        self.steps = []

    def add_step(self, content):
        self.steps.append(Step(content))


class Step(object):

    def __init__(self, content):
        self.keyword = content[0]
        self.args = content[1:]
