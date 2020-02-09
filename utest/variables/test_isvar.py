import unittest

from robot.variables import (contains_var, is_dict_var, is_list_var,
                             is_scalar_var, is_var)

SCALARS = ['${var}', '${  v A  R }']
LISTS = ['@{var}', '@{  v A  R }']
DICTS = ['&{var}', '&{  v A  R }']
NOKS = ['var', '$var', '${var', '${va}r', '@{va}r', '@var', '%{var}', ' ${var}',
        '@{var} ', '\\${var}', '\\\\${var}', 42, None, ['${var}'], unittest]


class TestIsVar(unittest.TestCase):

    def test_is_var(self):
        for ok in SCALARS + LISTS:
            assert is_var(ok)
            assert is_var(ok + '=', allow_assign_mark=True)
            assert is_var(ok + ' =', allow_assign_mark=True)
        for nok in NOKS:
            assert not is_var(nok)

    def test_is_scalar_var(self):
        for ok in SCALARS:
            assert is_scalar_var(ok)
            assert is_scalar_var(ok + '=', allow_assign_mark=True)
            assert is_scalar_var(ok + ' =', allow_assign_mark=True)
        for nok in NOKS + LISTS + DICTS:
            assert not is_scalar_var(nok)

    def test_is_list_var(self):
        for ok in LISTS:
            assert is_list_var(ok)
            assert is_list_var(ok + '=', allow_assign_mark=True)
            assert is_list_var(ok + ' =', allow_assign_mark=True)
        for nok in NOKS + SCALARS + DICTS:
            assert not is_list_var(nok)

    def test_is_dict_var(self):
        for ok in DICTS:
            assert is_dict_var(ok)
            assert is_dict_var(ok + '=', allow_assign_mark=True)
            assert is_dict_var(ok + ' =', allow_assign_mark=True)
        for nok in NOKS + SCALARS + LISTS:
            assert not is_dict_var(nok)

    def test_contains_var(self):
        for ok in SCALARS + LISTS + ['hi ${var}', '@{x}y', r'\${no ${yes}!']:
            assert contains_var(ok)
        for nok in [None, 42, unittest, '', 'nothing', '${no', '*{not}']:
            assert not contains_var(nok)


if __name__ == '__main__':
    unittest.main()
