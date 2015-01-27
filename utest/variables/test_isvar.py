import unittest

from robot.variables import contains_var, is_list_var, is_scalar_var, is_var

from test_variables import SCALARS, LISTS, NOKS


class TestIsVar(unittest.TestCase):

    def test_is_var(self):
        for ok in SCALARS + LISTS:
            assert is_var(ok)
        for nok in NOKS:
            assert not is_var(nok)

    def test_is_scalar_var(self):
        for ok in SCALARS:
            assert is_scalar_var(ok)
        for nok in LISTS + NOKS:
            assert not is_scalar_var(nok)

    def test_is_list_var(self):
        for ok in LISTS:
            assert is_list_var(ok)
        for nok in SCALARS + NOKS:
            assert not is_list_var(nok)

    def test_contains_var(self):
        for ok in SCALARS + LISTS + ['hi ${var}', '@{x}y', '${no ${yes}!']:
            assert contains_var(ok)
        for nok in [None, 42, unittest, '', 'nothing', '${no', '*{not}']:
            assert not contains_var(nok)


if __name__ == '__main__':
    unittest.main()
