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


import types
import os
import sys

from unic import unic


if sys.platform.startswith('java'):
    from java.util import HashMap


def dict2map(dictionary):
    if not sys.platform.startswith('java'):
        return dictionary
    map = HashMap()
    for key, value in dictionary.items():
        map.put(key, value)
    return map


# FIXME: Remove
def to_list(item):
    if item is None:
        return []
    return list(item)


_type_dict = dict([ (getattr(types,attr), attr) for attr in dir(types)
                    if not attr.startswith('_') and attr != 'StringTypes' ])

_printable_type_mapping = {
  'StringType'     : 'string',
  'UnicodeType'    : 'string',
  'DictionaryType' : 'dictionary',
  'ObjectType'     : 'object',
  'NoneType'       : 'None',
  'TupleType'      : 'list',
  'ListType'       : 'list',
  'IntType'        : 'integer',
  'LongType'       : 'integer',
  'BooleanType'    : 'boolean',
  'FloatType'      : 'floating point number',
}


def type_as_str(item, printable=False):
    try:
        ret = _type_dict[type(item)]
    except KeyError:
        ret = str(type(item))
    if printable and _printable_type_mapping.has_key(ret):
        ret = _printable_type_mapping[ret]
    return ret


def safe_repr(item):
    try:
        return unic(repr(item))
    except UnicodeError:
        return repr(unic(item))
