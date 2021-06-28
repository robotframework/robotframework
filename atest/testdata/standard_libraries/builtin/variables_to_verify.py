from collections import OrderedDict
import os
import sys

try:
    ascii
except NameError:
    ascii = repr

if os.name == 'java':
    from java.lang import String
    from java.util import Hashtable, Vector
    import jarray


PY3_OR_IPY = sys.version_info[0] > 2 or sys.platform == 'cli'


def get_variables():
    variables = dict(
        BYTES_WITHOUT_NON_ASCII=b'hyva',
        BYTES_WITH_NON_ASCII=b'\xe4',
        TUPLE_0=(),
        TUPLE_1=(u'a',),
        TUPLE_2=(u'a', 2),
        TUPLE_3=('a', 'b', 'c'),
        LIST=['a', 'b', 'cee', 'b', 42],
        LIST_0=[],
        LIST_1=['a'],
        LIST_2=['a', 2],
        LIST_3=['a', 'b', 'c'],
        LIST_4=['\ta', '\na', 'b ', 'b \t', '\tc\n'],
        DICT={u'a': 1, u'A': 2, u'\xe4': 3, u'\xc4': 4},
        ORDERED_DICT=OrderedDict([('a', 1), ('A', 2), (u'\xe4', 3), (u'\xc4', 4)]),
        DICT_0={},
        DICT_1={'a': 1},
        DICT_2={'a': 1, 2: 'b'},
        DICT_3={'a': 1, 'b': 2, 'c': 3},
        DICT_4={'\ta': 1, 'a b': 2, '  c': 3, 'dd\n\t': 4, '\nak \t': 5},
        DICT_5={' a': 0, '\ta': 1, 'a\t': 2, '\nb': 3, 'd\t': 4, '\td\n': 5, 'e   e': 6},
    )
    variables['ASCII_DICT'] = ascii(variables['DICT'])
    variables['PREPR_DICT1'] = "{'a': 1}" if PY3_OR_IPY else "{b'a': 1}"
    variables['U'] = '' if PY3_OR_IPY else 'u'
    if os.name == 'java':
        variables.update(get_java_variables(**variables))
    return variables


def get_java_variables(DICT_1, DICT_2, DICT_3, LIST_1, LIST_2, LIST_3, **extra):
    return dict(
        STRING_0=String(),
        STRING_1=String('a'),
        STRING_2=String('ab'),
        STRING_3=String('abc'),
        HASHTABLE_0=Hashtable(),
        HASHTABLE_1=create_hashtable(DICT_1),
        HASHTABLE_2=create_hashtable(DICT_2),
        HASHTABLE_3=create_hashtable(DICT_3),
        VECTOR_0=Vector(),
        VECTOR_1=Vector(LIST_1),
        VECTOR_2=Vector(LIST_2),
        VECTOR_3=Vector(LIST_3),
        ARRAY_0=jarray.array([], String),
        ARRAY_1=jarray.array([str(i) for i in LIST_1], String),
        ARRAY_2=jarray.array([str(i) for i in LIST_2], String),
        ARRAY_3=jarray.array([str(i) for i in LIST_3], String)
    )


def create_hashtable(dictionary):
    ht=Hashtable()
    for key, value in dictionary.items():
        ht.put(key, value)
    return ht
