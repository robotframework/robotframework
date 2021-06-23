import unittest
import warnings

from robot.variables import (contains_variable,
                             is_variable, is_assign,
                             is_scalar_variable, is_scalar_assign,
                             is_list_variable, is_list_assign,
                             is_dict_variable, is_dict_assign,
                             search_variable)
from robot.utils.asserts import assert_equal


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
            assert search_variable(ok).is_variable()
            assert not is_variable(' ' + ok)
            assert not is_variable(ok + '=')
        for nok in NOKS:
            assert not is_variable(nok)
            assert not search_variable(nok, identifiers='$@&',
                                       ignore_errors=True).is_variable()

    def test_is_scalar_variable(self):
        for ok in SCALARS:
            assert is_scalar_variable(ok)
            assert is_scalar_variable(ok + '[item]')
            assert search_variable(ok).is_variable()
            assert not is_scalar_variable(' ' + ok)
            assert not is_scalar_variable(ok + '=')
        for nok in NOKS + LISTS + DICTS:
            assert not is_scalar_variable(nok)
            assert not search_variable(nok, ignore_errors=True).is_scalar_variable()

    def test_is_list_variable(self):
        for ok in LISTS:
            assert is_list_variable(ok)
            assert search_variable(ok).is_list_variable()
            assert is_list_variable(ok + '[item]')
            assert not is_list_variable(' ' + ok)
            assert not is_list_variable(ok + '=')
        for nok in NOKS + SCALARS + DICTS:
            assert not is_list_variable(nok)
            assert not search_variable(nok, ignore_errors=True).is_list_variable()

    def test_is_dict_variable(self):
        for ok in DICTS:
            assert is_dict_variable(ok)
            assert search_variable(ok).is_dict_variable()
            assert is_dict_variable(ok + '[item]')
            assert not is_dict_variable(' ' + ok)
            assert not is_dict_variable(ok + '=')
        for nok in NOKS + SCALARS + LISTS:
            assert not is_dict_variable(nok)
            assert not search_variable(nok, ignore_errors=True).is_dict_variable()

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

    def test_deprecated_utils(self):
        from robot.variables import (is_var, is_scalar_var, is_list_var,
                                     is_dict_var, contains_var)
        for util, inp in [(is_var, '${x}'),
                          (is_scalar_var, '${x}'),
                          (is_list_var, '@{x}'),
                          (is_dict_var, '&{x}'),
                          (contains_var, 'x${x}x')]:
            with warnings.catch_warnings(record=True) as w:
                assert util(inp)
                assert not util('xxx')
                assert_equal(w[0].message.args[0], util.__doc__)
                assert_equal(w[0].category, UserWarning)


class TestIsAssign(unittest.TestCase):

    def test_is_assign(self):
        for ok in SCALARS + LISTS + DICTS:
            assert is_assign(ok)
            assert search_variable(ok).is_assign()
            assert is_assign(ok + '=', allow_assign_mark=True)
            assert is_assign(ok + ' =', allow_assign_mark=True)
            assert not is_assign(ok + '[item]')
            assert not is_assign(' ' + ok)
        for nok in NOK_ASSIGNS:
            assert not is_assign(nok)
            assert not search_variable(nok, ignore_errors=True).is_assign()

    def test_is_scalar_assign(self):
        for ok in SCALARS:
            assert is_scalar_assign(ok)
            assert search_variable(ok).is_scalar_assign()
            assert is_scalar_assign(ok + '=', allow_assign_mark=True)
            assert is_scalar_assign(ok + ' =', allow_assign_mark=True)
            assert not is_scalar_assign(ok + '[item]')
            assert not is_scalar_assign(' ' + ok)
        for nok in NOK_ASSIGNS + LISTS + DICTS:
            assert not is_scalar_assign(nok)
            assert not search_variable(nok, ignore_errors=True).is_scalar_assign()

    def test_is_list_assign(self):
        for ok in LISTS:
            assert is_list_assign(ok)
            assert search_variable(ok).is_list_assign()
            assert is_list_assign(ok + '=', allow_assign_mark=True)
            assert is_list_assign(ok + ' =', allow_assign_mark=True)
            assert not is_list_assign(ok + '[item]')
            assert not is_list_assign(' ' + ok)
        for nok in NOK_ASSIGNS + SCALARS + DICTS:
            assert not is_list_assign(nok)
            assert not search_variable(nok, ignore_errors=True).is_list_assign()

    def test_is_dict_assign(self):
        for ok in DICTS:
            assert is_dict_assign(ok)
            assert search_variable(ok).is_dict_assign()
            assert is_dict_assign(ok + '=', allow_assign_mark=True)
            assert is_dict_assign(ok + ' =', allow_assign_mark=True)
            assert not is_dict_assign(ok + '[item]')
            assert not is_dict_assign(' ' + ok)
        for nok in NOK_ASSIGNS + SCALARS + LISTS:
            assert not is_dict_assign(nok)
            assert not search_variable(nok, ignore_errors=True).is_dict_assign()


if __name__ == '__main__':
    unittest.main()
