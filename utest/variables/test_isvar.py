import unittest

from robot.variables import (contains_variable,
                             is_variable, is_assign,
                             is_scalar_variable, is_scalar_assign,
                             is_list_variable, is_list_assign,
                             is_dict_variable, is_dict_assign)

SCALARS = ['${var}', '${  v A  R }']
LISTS = ['@{var}', '@{  v A  R }']
DICTS = ['&{var}', '&{  v A  R }']
NOKS = ['', 'nothing', '$not', '${not', '@not', '&{not', '${not}[oops',
        '%{not}', '*{not}', r'\${var}', r'\\\${var}', 42, None, ['${var}']]
NOK_ASSIGNS = NOKS + ['${${internal}}', '${var}[item]',
                      '@{${internal}}', '@{var}[item]',
                      '&{${internal}}', '&{var}[item]']


class TestIsVariable(unittest.TestCase):

    def test_is_variable(self):
        for ok in SCALARS + LISTS + DICTS:
            assert is_variable(ok)
            assert is_variable(ok + '[item]')
            assert not is_variable(' ' + ok)
            assert not is_variable(ok + '=')
        for nok in NOKS:
            assert not is_variable(nok)

    def test_is_scalar_variable(self):
        for ok in SCALARS:
            assert is_scalar_variable(ok)
            assert is_scalar_variable(ok + '[item]')
            assert not is_scalar_variable(' ' + ok)
            assert not is_scalar_variable(ok + '=')
        for nok in NOKS + LISTS + DICTS:
            assert not is_scalar_variable(nok)

    def test_is_list_variable(self):
        for ok in LISTS:
            assert is_list_variable(ok)
            assert not is_list_variable(ok + '[item]')
            assert not is_list_variable(' ' + ok)
            assert not is_list_variable(ok + '=')
        for nok in NOKS + SCALARS + DICTS:
            assert not is_list_variable(nok)

    def test_is_dict_variable(self):
        for ok in DICTS:
            assert is_dict_variable(ok)
            assert not is_dict_variable(ok + '[item]')
            assert not is_dict_variable(' ' + ok)
            assert not is_dict_variable(ok + '=')
        for nok in NOKS + SCALARS + LISTS:
            assert not is_dict_variable(nok)

    def test_contains_variable(self):
        for ok in SCALARS + LISTS + DICTS + [r'\${no ${yes}!']:
            assert contains_variable(ok)
            assert contains_variable(ok + '[item]')
            assert contains_variable('hello %s world' % ok)
            assert contains_variable('hello %s[item] world' % ok)
            assert contains_variable(' ' + ok)
            assert contains_variable(r'\\' + ok)
            assert contains_variable(ok + '=')
            assert contains_variable(ok + ok)
        for nok in NOKS:
            assert not contains_variable(nok)


class TestIsAssign(unittest.TestCase):

    def test_is_assign(self):
        for ok in SCALARS + LISTS + DICTS:
            assert is_assign(ok)
            assert is_assign(ok + '=', allow_assign_mark=True)
            assert is_assign(ok + ' =', allow_assign_mark=True)
            assert not is_assign(ok + '[item]')
            assert not is_assign(' ' + ok)
        for nok in NOK_ASSIGNS:
            assert not is_assign(nok)

    def test_is_scalar_assign(self):
        for ok in SCALARS:
            assert is_scalar_assign(ok)
            assert is_scalar_assign(ok + '=', allow_assign_mark=True)
            assert is_scalar_assign(ok + ' =', allow_assign_mark=True)
            assert not is_scalar_assign(ok + '[item]')
            assert not is_scalar_assign(' ' + ok)
        for nok in NOK_ASSIGNS + LISTS + DICTS:
            assert not is_scalar_assign(nok)

    def test_is_list_assign(self):
        for ok in LISTS:
            assert is_list_assign(ok)
            assert is_list_assign(ok + '=', allow_assign_mark=True)
            assert is_list_assign(ok + ' =', allow_assign_mark=True)
            assert not is_list_assign(ok + '[item]')
            assert not is_list_assign(' ' + ok)
        for nok in NOK_ASSIGNS + SCALARS + DICTS:
            assert not is_list_assign(nok)

    def test_is_dict_assign(self):
        for ok in DICTS:
            assert is_dict_assign(ok)
            assert is_dict_assign(ok + '=', allow_assign_mark=True)
            assert is_dict_assign(ok + ' =', allow_assign_mark=True)
            assert not is_dict_assign(ok + '[item]')
            assert not is_dict_assign(' ' + ok)
        for nok in NOK_ASSIGNS + SCALARS + LISTS:
            assert not is_dict_assign(nok)


if __name__ == '__main__':
    unittest.main()
