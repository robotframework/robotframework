import re

from robot import utils


class _TablePopulator(object):

    def __init__(self, datafile):
        self._table = self._get_table(datafile)
        self._current_populator = None

    def add(self, row):
        if self._is_continuing_row(row):
            self._current_populator.add(self._values_from(row))
        else:
            if self._current_populator:
                self._current_populator.populate()
            self._current_populator = self._get_populator(row)

    def _is_continuing_row(self, row):
        return row[0] == '...'

    def populate(self):
        if self._current_populator:
            self._current_populator.populate()


class SettingTablePopulator(_TablePopulator):
    attrs_by_name = utils.NormalizedDict({'Documentation': 'doc',
                                          'Document': 'doc',
                                          'Suite Setup': 'suite_setup',
                                          'Suite Precondition': 'suite_setup',
                                          'Suite Teardown': 'suite_teardown',
                                          'Suite Postcondition': 'suite_teardown',
                                          'Test Setup': 'test_setup',
                                          'Test Precondition': 'test_setup',
                                          'Test Teardown': 'test_teardown',
                                          'Test Postcondition': 'test_teardown',
                                          'Force Tags': 'force_tags',
                                          'Default Tags': 'default_tags',
                                          'Test Timeout': 'test_timeout'})

    import_setters_by_name = utils.NormalizedDict({'Library': 'add_library',
                                                   'Resource': 'add_resource',
                                                   'Variables': 'add_variables'})

    def _get_table(self, datafile):
        return datafile.setting_table

    def _values_from(self, row):
        return row[1:]

    def _get_populator(self, row):
        return PropertyPopulator(self._get_setter(row[0]), row[1:])

    def _get_setter(self, setting_name):
        if setting_name in self.import_setters_by_name:
            attr_name = self.import_setters_by_name[setting_name]
            return getattr(self._table, attr_name)
        attr_name = self.attrs_by_name[setting_name]
        return getattr(self._table, attr_name).set


class VariableTablePopulator(_TablePopulator):

    def _get_table(self, datafile):
        return datafile.variable_table

    def _get_populator(self, row):
        return VariablePopulator(self._table.add, row)

    def _values_from(self, row):
        return row


class TestTablePopulator(SettingTablePopulator): pass
class KeywordTablePopulator(SettingTablePopulator): pass


class PropertyPopulator(object):

    def __init__(self, setter, initial_value):
        self._setter = setter
        self._value = initial_value

    def add(self, row):
        self._value.extend(row)

    def populate(self):
        self._setter(self._value)


class VariablePopulator(PropertyPopulator):
    def populate(self):
        self._setter(self._value[0], self._value[1:])



class Populator(object):
    _whitespace_regexp = re.compile('\s+')
    _null_populator = type('NullTablePopulator', (), 
                           {'add': lambda self, row: None,
                            'eof': lambda self: None})()
    populators = utils.NormalizedDict({'Setting':       SettingTablePopulator,
                                       'Settings':      SettingTablePopulator,
                                       'Metadata':      SettingTablePopulator,
                                       'Variable':      VariableTablePopulator,
                                       'Variables':     VariableTablePopulator,
                                       'Test Case':     TestTablePopulator,
                                       'Test Cases':    TestTablePopulator,
                                       'Keyword':       KeywordTablePopulator,
                                       'Keywords':      KeywordTablePopulator,
                                       'User Keyword':  KeywordTablePopulator,
                                       'User Keywords': KeywordTablePopulator})

    def __init__(self, datafile, path):
        self._datafile = datafile
        self._datafile.source = path
        self._current_populator = self._null_populator

    def start_table(self, name):
        try:
            self._current_populator = self.populators[name](self._datafile)
        except KeyError:
            self._current_populator = self._null_populator
        return self._current_populator is not self._null_populator

    def add(self, row):
        if row:
            self._current_populator.add(row)

    def eof(self):
        self._current_populator.populate()

    def _collapse_whitespace(self, value):
        return self._whitespace_regexp.sub(' ', value).strip()
