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


# TODO: Various tasks
# - Rename this module so that it is not confused with standard json module
# - Consider moving under utils
# - Cleanup


def encode_basestring(string):
    def get_matching_char(c):
        val = ord(c)
        if val < 127 and val > 31:
            return c
        return '\\u' + hex(val)[2:].rjust(4,'0')
    # TODO: Our log doesn't contain all these control chars
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    string = string.replace('\b', '\\b')
    string = string.replace('\f', '\\f')
    string = string.replace('\n', '\\n')
    string = string.replace('\r', '\\r')
    string = string.replace('\t', '\\t')
    return '"%s"' % ''.join(get_matching_char(c) for c in string)

def json_dump(data, output, mapping=None):
    if data is None:
        output.write('null')
    elif isinstance(data, dict):
        output.write('{')
        for index, key in enumerate(data):
            json_dump(key, output, mapping)
            output.write(':')
            json_dump(data[key], output, mapping)
            if index < len(data)-1:
                output.write(',')
        output.write('}')
    elif isinstance(data, (list, tuple)):
        output.write('[')
        for index, item in enumerate(data):
            json_dump(item, output, mapping)
            if index < len(data)-1:
                output.write(',')
        output.write(']')
    elif mapping and data in mapping:
        output.write(mapping[data])
    elif isinstance(data, (int, long)):
        output.write(str(data))
    elif isinstance(data, basestring):
        output.write(encode_basestring(data))
    else:
        raise Exception('Data type (%s) serialization not supported' % type(data))
