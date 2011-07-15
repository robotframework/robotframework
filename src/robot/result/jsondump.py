#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


class JsonDumper(object):

    def __init__(self, output):
        self._output = output
        self._data_dumpers = [_IterableDumper(self), _MappingDumper(self),
                              _StringDumper(self), _IntegerDumper(self),
                              _DictDumper(self), _NoneDumper(self)]

    def dump(self, data, mapping=None):
        for dumper in self._data_dumpers:
            dumper.add_mapping(mapping)
            if dumper.handles(data):
                dumper.dump(data)
                return
        raise ValueError('Dumping %s not supported' % type(data))

    def write(self, data):
        self._output.write(data)


class _DataDumper(object):

    def __init__(self, jsondumper):
        self._jsondumper = jsondumper
        self._mapping = {}

    def add_mapping(self, mapping):
        self._mapping = mapping or {}

    def _dump(self, data):
        self._jsondumper.dump(data, self._mapping)

    def _write(self, data):
        self._jsondumper.write(data)


class _StringDumper(_DataDumper):
    _replace = [('\\', '\\\\'), ('"', '\\"'), ('\t', '\\t'),
                ('\n', '\\n'), ('\r', '\\r')]

    def handles(self, data):
        return isinstance(data, basestring)

    def dump(self, string):
        for char, repl in self._replace:
            string = string.replace(char, repl)
        self._write('"%s"' % ''.join(self._encode_char(c) for c in string))

    def _encode_char(self, char):
        val = ord(char)
        if 31 < val < 127:
            return char
        return '\\u' + hex(val)[2:].rjust(4, '0')


class _IntegerDumper(_DataDumper):

    def handles(self, data):
        return isinstance(data, (int, long))

    def dump(self, data):
        self._write(str(data))


class _DictDumper(_DataDumper):

    def handles(self, data):
        return isinstance(data, dict)

    def dump(self, data):
        self._write('{')
        last_index = len(data) - 1
        for index, key in enumerate(sorted(data)):
            self._dump(key)
            self._write(':')
            self._dump(data[key])
            if index < last_index:
                self._write(',')
        self._write('}')


class _IterableDumper(_DataDumper):

    def handles(self, data):
        try:
            iter(data)
        except TypeError:
            return False
        return not isinstance(data, (basestring, dict))

    def dump(self, data):
        self._write('[')
        last_index = len(data) - 1
        for index, item in enumerate(data):
            self._dump(item)
            if index < last_index:
                self._write(',')
        self._write(']')


class _MappingDumper(_DataDumper):

    def handles(self, data):
        try:
            return data in self._mapping
        except TypeError:
            return False

    def dump(self, data):
        self._write(self._mapping[data])


class _NoneDumper(_DataDumper):

    def handles(self, data):
        return data is None

    def dump(self, data):
        self._write('null')
