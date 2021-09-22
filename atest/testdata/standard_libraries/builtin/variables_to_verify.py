from collections import OrderedDict


def get_variables():
    variables = dict(
        BYTES_WITHOUT_NON_ASCII=b'hyva',
        BYTES_WITH_NON_ASCII=b'\xe4',
        TUPLE_0=(),
        TUPLE_1=('a',),
        TUPLE_2=('a', 2),
        TUPLE_3=('a', 'b', 'c'),
        LIST=['a', 'b', 'cee', 'b', 42],
        LIST_0=[],
        LIST_1=['a'],
        LIST_2=['a', 2],
        LIST_3=['a', 'b', 'c'],
        LIST_4=['\ta', '\na', 'b ', 'b \t', '\tc\n'],
        DICT={'a': 1, 'A': 2, '\xe4': 3, '\xc4': 4},
        ORDERED_DICT=OrderedDict([('a', 1), ('A', 2), ('\xe4', 3), ('\xc4', 4)]),
        DICT_0={},
        DICT_1={'a': 1},
        DICT_2={'a': 1, 2: 'b'},
        DICT_3={'a': 1, 'b': 2, 'c': 3},
        DICT_4={'\ta': 1, 'a b': 2, '  c': 3, 'dd\n\t': 4, '\nak \t': 5},
        DICT_5={' a': 0, '\ta': 1, 'a\t': 2, '\nb': 3, 'd\t': 4, '\td\n': 5, 'e   e': 6},
        PREPR_DICT1="{'a': 1}"
    )
    variables['ASCII_DICT'] = ascii(variables['DICT'])
    return variables
