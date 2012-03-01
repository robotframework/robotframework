import unittest

from robot.errors import DataError
from robot.running.variableassigner import VariableAssigner
from robot.utils.asserts import assert_equals, assert_raises_with_msg


class TestResolveAssignment(unittest.TestCase):

    def test_one_scalar(self):
        self._verify(['${var}'])

    def test_multiple_scalars(self):
        self._verify('${v1} ${v2} ${v3}'.split())

    def test_list(self):
        self._verify(['@{list}'])

    def test_scalars_and_list(self):
        self._verify('${v1} ${v2} @{list}'.split())

    def test_equal_sign(self):
        self._verify(['${var} ='])
        self._verify('${v1} ${v2} @{list}='.split())

    def test_equal_sign_in_wrong_place(self):
        msg = "Assign mark '=' can be used only with the last variable."
        assert_raises_with_msg(DataError, msg,
                               VariableAssigner, ['${v1}=','${v2}'])
        assert_raises_with_msg(DataError, msg,
                               VariableAssigner, ['${v1} =','@{v2} ='])

    def test_init_list_in_wrong_place_raises(self):
        msg = 'Only the last variable to assign can be a list variable.'
        assert_raises_with_msg(DataError, msg,
                               VariableAssigner, ['@{list}','${str}'])

    def _verify(self, assign):
        assigner = VariableAssigner(assign)
        assign[-1] = assign[-1].rstrip('= ')
        if assign[-1][0] == '$':
            exp_list = None
        else:
            exp_list = assign.pop()
        assert_equals(assigner.scalar_vars, assign)
        assert_equals(assigner.list_var, exp_list)


if __name__ == '__main__':
    unittest.main()
