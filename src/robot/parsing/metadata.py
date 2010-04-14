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


import os
import sys

from robot import utils
from robot.errors import DataError


class _Metadata:

    def __init__(self, metadata=None):
        self._data = {}
        for name in self._names.values():
            self._data[name.replace(' ','')] = None
        if metadata is not None:
            for item in metadata:
                self.set(item)

    def set(self, item):
        try:
            name = self._names[utils.normalize(item.name)].replace(' ', '')
        except KeyError:
            self._report_invalid_meta(item)
        else:
            if self._data[name] is None:
                self._data[name] = item.value
            else:
                self._data[name].extend(item.value)

    def _report_invalid_meta(self, item):
        name = self.__class__.__name__.replace('Metadata','')
        name = utils.printable_name(name, code_style=True)
        available = self._get_available_names()
        msg = "%s does not have metadata '%s'. Available: %s"
        item.report_invalid_syntax(msg % (name, item.name, available))

    def _get_available_names(self):
        names = dict([ (name, 1) for name in self._names.values() ]).keys()
        names.sort()
        return utils.seq2str(names)

    def get(self, key, default=None):
        value = self._data[key]
        if value is None:
            return default
        if key == 'Documentation':
            return ' '.join(value)
        return value

    def __getitem__(self, key):
        return self.get(key)


class TestCaseMetadata(_Metadata):
    _names = { 'documentation': 'Documentation',
               'document': 'Documentation',
               'setup': 'Setup',
               'precondition': 'Setup',
               'teardown': 'Teardown',
               'postcondition': 'Teardown',
               'tags': 'Tags',
               'timeout': 'Timeout' }


class UserKeywordMetadata(_Metadata):
    _names = { 'documentation': 'Documentation',
               'document': 'Documentation',
               'arguments': 'Arguments',
               'return': 'Return',
               'timeout': 'Timeout' }


class TestCaseFileMetadata(_Metadata):
    _names = { 'documentation': 'Documentation',
               'document': 'Documentation',
               'suitesetup': 'Suite Setup',
               'suiteprecondition': 'Suite Setup',
               'suiteteardown': 'Suite Teardown',
               'suitepostcondition': 'Suite Teardown',
               'testsetup': 'Test Setup',
               'testprecondition': 'Test Setup',
               'testteardown': 'Test Teardown',
               'testpostcondition': 'Test Teardown',
               'defaulttags': 'Default Tags',
               'forcetags': 'Force Tags',
               'testtimeout': 'Test Timeout' }

    def __init__(self, rawdata=None):
        _Metadata.__init__(self)
        self.user_metadata = {}
        self.imports = []
        if rawdata is not None:
            self._set_rawdata(rawdata)

    def _set_rawdata(self, rawdata):
        for item in rawdata.settings:
            name = item.name.lower()
            if name in ['library', 'resource', 'variables']:
                self.imports.append(ImportSetting(item))
            elif name.startswith('meta:'):
                self._set_user_metadata(item.name[5:].strip(), item.value)
            else:
                self.set(item)

    def _set_user_metadata(self, name, value):
        name = utils.printable_name(name)
        value = ' '.join(value)
        if self.user_metadata.has_key(name):
            value = '%s %s' % (self.user_metadata[name], value)
        self.user_metadata[name] = value


class TestSuiteInitFileMetadata(TestCaseFileMetadata):
    _deprecated_metadata = ['testsetup', 'testteardown', 'defaulttags',
                            'testtimeout']

    def set(self, item):
        TestCaseFileMetadata.set(self, item)
        if utils.normalize(item.name) in self._deprecated_metadata:
            msg = "Using setting '%s' in init file is deprecated and will be " \
                    "removed in the next major release." % (item.name)
            item.report_invalid_syntax(msg, 'WARN')


class ImportSetting:

    def __init__(self, item):
        self._item = item
        self.name = item.name = utils.normalize(item.name).capitalize()
        self.value = None

    def original_value(self):
        return self._item.copy().value

    def replace_variables(self, variables):
        item = self._item.copy()
        try:
            self.value = variables.replace_list(item.value)
        except DataError:
            raise DataError("Replacing variables from setting '%s' failed: %s"
                            % (self.name, utils.get_error_message()))
        if len(self.value) == 0:
            raise DataError("Setting '%s' requires a value" % self.name)
        if self.name == 'Resource' and len(self.value) > 1:
            raise DataError('Invalid resource import parameters: %s' % utils.seq2str2(self.value))
        basedir = utils.get_directory(item._parent._source)
        self.value[0] = self._get_path(self.name, self.value[0], basedir)

    def resolve_name(self, name):
        """Returns absolute path to file if name points to one, otherwise return name unchanged."""
        return self._get_path(self.name, name,
                              utils.get_directory(self._item._parent._source))

    def _get_path(self, name, path, basedir):
        if name == 'Library' and not self._is_library_by_path(path, basedir):
            return path
        try:
            path = self._resolve_path(path.replace('/', os.sep), basedir)
        except DataError:
            if name == 'Variables': name = 'Variable file'
            if name == 'Resource': name = 'Resource file'
            raise DataError("%s '%s' does not exist" % (name, path))
        if name in ['Variables','Library']:
            dirname, filename = os.path.split(os.path.normpath(path))
            path = os.path.join(utils.normpath(dirname), filename)
        else:
            path = utils.normpath(path)
        return path

    def _is_library_by_path(self, path, basedir):
        if os.path.splitext(path)[1].lower() in ['.py','.java','.class']:
            return os.path.isfile(os.path.join(basedir, path))
        if not path.endswith('/'):
            return False
        init = os.path.join(basedir, path.replace('/',os.sep), '__init__.py')
        return os.path.isfile(init)

    def _resolve_path(self, respath, basedir):
        for base in [basedir] + sys.path:
            if not os.path.isdir(base):
                continue
            path = os.path.join(base, respath)
            if os.path.exists(path):
                return path
        raise DataError()

    def report_invalid_syntax(self):
        self._item.report_invalid_syntax()
