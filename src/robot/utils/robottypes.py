#  Copyright 2008 Nokia Siemens Networks Oyj
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

from robot.errors import FrameworkError
from match import eq_any


_LIST_TYPES = [ types.ListType, types.TupleType ]
if os.name == 'java':
    _LIST_TYPES.append(types.ArrayType)


def is_list(item):
    # TODO: Should support also other iterables incl. java.lang.Vector
    return type(item) in _LIST_TYPES

def is_tuple(item):
    return type(item) is types.TupleType

def is_scalar(item):
    return not is_list(item)

def is_str(item):
    return type(item) in types.StringTypes

def is_integer(item):
    return type(item) in [ types.IntType, types.LongType ]

def is_number(item):
    return type(item) in [ types.IntType, types.LongType, types.FloatType ]

def is_boolean(item):
    return type(item) is type(True) # No BooleanType in Jython 2.2a1

def is_list_of_str(item):
    if not is_list(item): return False
    for i in item:
        if not is_str(i): return False
    return True


_default_true_strs = ['True', 'Yes']
_default_false_strs = ['False', 'No']

def _get_boolean_strs(given, defaults):
        if given is None: 
            return defaults
        return given + defaults

def to_boolean(value, true_strs=None, false_strs=None, default=False):
    if is_boolean(value):
        return value 
    if is_number(value):
        return value != 0
    if is_str(value):
        true_strs =_get_boolean_strs(true_strs, _default_true_strs)
        false_strs =_get_boolean_strs(false_strs, _default_false_strs)
        if eq_any(value, true_strs):
            return True
        if eq_any(value, false_strs):
            return False
    return default


def to_list(item):
    if item is None:
        return []
    if not is_list(item):
        raise FrameworkError('Expected list, tuple or None, got %s'
                             % type_as_str(item, True))
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
  'ArrayType'      : 'array'
}
                       

def type_as_str(item, printable=False):
    try:
        ret = _type_dict[type(item)]
    except KeyError:
        ret = str(type(item))
    if printable and _printable_type_mapping.has_key(ret):
        ret = _printable_type_mapping[ret]
    return ret


def unic(item):
    """Convert non-strings to unicode."""
    typ = type(item)
    if typ is types.UnicodeType:
        return item
    if typ is types.StringType:
        # There's some weird bug in Jython that requires this to unicode to
        # work but this causes other issues........ =/
        if os.name == 'java':
            return item
        return item.decode('UTF-8', 'ignore')
    # Workaround for bug in Jython 2.2a1
    if os.name == 'java' and sys.version_info[:4] == (2,2,0,'alpha'):
        return str(item)
    return unicode(item)
