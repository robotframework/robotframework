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


def json_dump(data, output, mappings=None):
    if data is None:
        output.write('null')
    elif isinstance(data, dict):
        output.write('{')
        last_index = len(data) - 1
        for index, key in enumerate(sorted(data)):
            json_dump(key, output, mappings)
            output.write(':')
            json_dump(data[key], output, mappings)
            if index < last_index:
                output.write(',')
        output.write('}')
    elif _iterable(data):
        output.write('[')
        last_index = len(data) - 1
        for index, item in enumerate(data):
            json_dump(item, output, mappings)
            if index < last_index:
                output.write(',')
        output.write(']')
    elif mappings and data in mappings:
        output.write(mappings[data])
    elif isinstance(data, (int, long)):
        output.write(str(data))
    elif isinstance(data, basestring):
        output.write(_encode_string(data))
    else:
        raise ValueError('jsondumping %s not supported' % type(data))


def _encode_string(string):
    for char, repl in [('\\', '\\\\'), ('"', '\\"'), ('\n', '\\n'),
                       ('\r', '\\r'), ('\t', '\\t')]:
        string = string.replace(char, repl)
    return '"%s"' % ''.join(_encode_char(c) for c in string)

def _encode_char(c):
    val = ord(c)
    if 31 < val < 127:
        return c
    return '\\u' + hex(val)[2:].rjust(4, '0')

def _iterable(item):
    if isinstance(item, basestring):
        return False
    try:
        iter(item)
    except TypeError:
        return False
    return True
