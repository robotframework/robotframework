#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


class Populator(object):
    """Explicit interface for all populators."""
    def add(self, row): raise NotImplementedError()
    def populate(self): raise NotImplementedError()


class CommentCacher(object):

    def __init__(self):
        self._init_comments()

    def _init_comments(self):
        self._comments = []

    def add(self, comment):
        self._comments.append(comment)

    def consume_comments_with(self, function):
        for c in self._comments:
            function(c)
        self._init_comments()


class _TablePopulator(Populator):

    def __init__(self, table):
        self._table = table
        self._populator = NullPopulator()
        self._comments = CommentCacher()

    def add(self, row):
        if self._is_cacheable_comment_row(row):
            self._comments.add(row)
        else:
            self._add(row)

    def _add(self, row):
        if not self._is_continuing(row):
            self._populator.populate()
            self._populator = self._get_populator(row)
        self._comments.consume_comments_with(self._populator.add)
        self._populator.add(row)

    def populate(self):
        self._comments.consume_comments_with(self._populator.add)
        self._populator.populate()

    def _is_continuing(self, row):
        return row.is_continuing() and self._populator

    def _is_cacheable_comment_row(self, row):
        return row.is_commented()


class SettingTablePopulator(_TablePopulator):

    def _get_populator(self, row):
        row.handle_old_style_metadata()
        setter = self._table.get_setter(row.head)
        return SettingPopulator(setter) if setter else NullPopulator()


class VariableTablePopulator(_TablePopulator):

    def _get_populator(self, row):
        return VariablePopulator(self._table.add, row.head)


class _StepContainingTablePopulator(_TablePopulator):

    def _is_continuing(self, row):
        return row.is_indented() and self._populator or row.is_commented()

    def _is_cacheable_comment_row(self, row):
        return row.is_commented() and isinstance(self._populator, NullPopulator)


class TestTablePopulator(_StepContainingTablePopulator):

    def _get_populator(self, row):
        return TestCasePopulator(self._table.add)


class KeywordTablePopulator(_StepContainingTablePopulator):

    def _get_populator(self, row):
        return UserKeywordPopulator(self._table.add)


class ForLoopPopulator(Populator):

    def __init__(self, for_loop_creator):
        self._for_loop_creator = for_loop_creator
        self._loop = None
        self._populator = NullPopulator()
        self._declaration = []

    def add(self, row):
        dedented_row = row.dedent()
        if not self._loop:
            declaration_ready = self._populate_declaration(row)
            if not declaration_ready:
                return
            self._loop = self._for_loop_creator(self._declaration)
        if not row.is_continuing():
            self._populator.populate()
            self._populator = StepPopulator(self._loop.add_step)
        self._populator.add(dedented_row)

    def _populate_declaration(self, row):
        if row.starts_for_loop() or row.is_continuing():
            self._declaration.extend(row.dedent().data)
            return False
        return True

    def populate(self):
        if not self._loop:
            self._for_loop_creator(self._declaration)
        self._populator.populate()


class _TestCaseUserKeywordPopulator(Populator):

    def __init__(self, test_or_uk_creator):
        self._test_or_uk_creator = test_or_uk_creator
        self._test_or_uk = None
        self._populator = NullPopulator()
        self._comments = CommentCacher()

    def add(self, row):
        if row.is_commented():
            self._comments.add(row)
            return
        if not self._test_or_uk:
            self._test_or_uk = self._test_or_uk_creator(row.head)
        dedented_row = row.dedent()
        if dedented_row:
            self._handle_data_row(dedented_row)

    def _handle_data_row(self, row):
        if not self._continues(row):
            self._populator.populate()
            self._populator = self._get_populator(row)
            self._flush_comments_with(self._populate_comment_row)
        else:
            self._flush_comments_with(self._populator.add)
        self._populator.add(row)

    def _populate_comment_row(self, crow):
        populator = StepPopulator(self._test_or_uk.add_step)
        populator.add(crow)
        populator.populate()

    def _flush_comments_with(self, function):
        self._comments.consume_comments_with(function)

    def populate(self):
        self._populator.populate()
        self._flush_comments_with(self._populate_comment_row)

    def _get_populator(self, row):
        if row.starts_test_or_user_keyword_setting():
            setter = self._setting_setter(row)
            return SettingPopulator(setter) if setter else NullPopulator()
        if row.starts_for_loop():
            return ForLoopPopulator(self._test_or_uk.add_for_loop)
        return StepPopulator(self._test_or_uk.add_step)

    def _continues(self, row):
        return row.is_continuing() and self._populator or \
            (isinstance(self._populator, ForLoopPopulator) and row.is_indented())

    def _setting_setter(self, row):
        setting_name = row.test_or_user_keyword_setting_name()
        return self._test_or_uk.get_setter(setting_name)


class TestCasePopulator(_TestCaseUserKeywordPopulator):
    _item_type = 'test case'


class UserKeywordPopulator(_TestCaseUserKeywordPopulator):
    _item_type = 'keyword'


class Comments(object):

    def __init__(self):
        self._crows = []

    def add(self, row):
        if row.comments:
            self._crows.append(row.comments)

    def formatted_value(self):
        rows = (' '.join(row).strip() for row in self._crows)
        return '\n'.join(rows)


class _PropertyPopulator(Populator):

    def __init__(self, setter):
        self._setter = setter
        self._value = []
        self._comments = Comments()

    def add(self, row):
        if not row.is_commented():
            self._add(row)
        self._comments.add(row)

    def _add(self, row):
        self._value.extend(row.dedent().data)


class VariablePopulator(_PropertyPopulator):

    def __init__(self, setter, name):
        _PropertyPopulator.__init__(self, setter)
        self._name = name

    def populate(self):
        self._setter(self._name, self._value,
                     self._comments.formatted_value())


class SettingPopulator(_PropertyPopulator):

    def populate(self):
        self._setter(self._value, self._comments.formatted_value())


class StepPopulator(_PropertyPopulator):

    def _add(self, row):
        self._value.extend(row.data)

    def populate(self):
        if self._value or self._comments:
            self._setter(self._value, self._comments.formatted_value())


class NullPopulator(Populator):
    def add(self, row): pass
    def populate(self): pass
    def __nonzero__(self): return False
