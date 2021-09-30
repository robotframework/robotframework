#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from robot.utils import PY2


class JsonWriter(object):

    def __init__(self, output, separator=''):
        self._writer = JsonDumper(output)
        self._separator = separator

    def write_json(self, prefix, data, postfix=';\n', mapping=None,
                   separator=True):
        self._writer.write(prefix)
        self._writer.dump(data, mapping)
        self._writer.write(postfix)
        self._write_separator(separator)

    def write(self, string, postfix=';\n', separator=True):
        self._writer.write(string + postfix)
        self._write_separator(separator)

    def _write_separator(self, separator):
        if separator and self._separator:
            self._writer.write(self._separator)


class JsonDumper(object):

    def __init__(self, output):
        self.write = output.write
        self._dumpers = (MappingDumper(self),
                         IntegerDumper(self),
                         TupleListDumper(self),
                         StringDumper(self),
                         NoneDumper(self),
                         DictDumper(self))

    def dump(self, data, mapping=None):
        for dumper in self._dumpers:
            if dumper.handles(data, mapping):
                dumper.dump(data, mapping)
                return
        raise ValueError('Dumping %s not supported.' % type(data))


class _Dumper(object):
    _handled_types = None

    def __init__(self, jsondumper):
        self._dump = jsondumper.dump
        self._write = jsondumper.write

    def handles(self, data, mapping):
        return isinstance(data, self._handled_types)

    def dump(self, data, mapping):
        raise NotImplementedError


class StringDumper(_Dumper):
    _handled_types = (str, unicode) if PY2 else str
    _search_and_replace = [('\\', '\\\\'), ('"', '\\"'), ('\t', '\\t'),
                           ('\n', '\\n'), ('\r', '\\r'), ('</', '\\x3c/')]

    def dump(self, data, mapping):
        self._write('"%s"' % (self._escape(data) if data else ''))

    def _escape(self, string):
        for search, replace in self._search_and_replace:
            if search in string:
                string = string.replace(search, replace)
        return string


class IntegerDumper(_Dumper):
    # Handles also bool
    _handled_types = (int, long) if PY2 else int

    def dump(self, data, mapping):
        self._write(str(data).lower())


class DictDumper(_Dumper):
    _handled_types = dict

    def dump(self, data, mapping):
        write = self._write
        dump = self._dump
        write('{')
        last_index = len(data) - 1
        for index, key in enumerate(sorted(data)):
            dump(key, mapping)
            write(':')
            dump(data[key], mapping)
            if index < last_index:
                write(',')
        write('}')


class TupleListDumper(_Dumper):
    _handled_types = (tuple, list)

    def dump(self, data, mapping):
        write = self._write
        dump = self._dump
        write('[')
        last_index = len(data) - 1
        for index, item in enumerate(data):
            dump(item, mapping)
            if index < last_index:
                write(',')
        write(']')


class MappingDumper(_Dumper):

    def handles(self, data, mapping):
        try:
            return mapping and data in mapping
        except TypeError:
            return False

    def dump(self, data, mapping):
        self._write(mapping[data])


class NoneDumper(_Dumper):

    def handles(self, data, mapping):
        return data is None

    def dump(self, data, mapping):
        self._write('null')
