import unittest

from robot.errors import DataError
from robot.variables import VariableAssignment
from robot.utils.asserts import assert_equal, assert_raises


class TestResolveAssignment(unittest.TestCase):

    def test_one_scalar(self):
        self._verify_valid(['${var}'])

    def test_multiple_scalars(self):
        self._verify_valid('${v1} ${v2} ${v3}'.split())

    def test_list(self):
        self._verify_valid(['@{list}'])

    def test_dict(self):
        self._verify_valid(['&{dict}'])

    def test_scalars_and_list(self):
        self._verify_valid('${v1} ${v2} @{list}'.split())
        self._verify_valid('@{list} ${v1} ${v2}'.split())
        self._verify_valid('${v1} @{list} ${v2}'.split())

    def test_equal_sign(self):
        self._verify_valid(['${var} ='])
        self._verify_valid('${v1} ${v2} @{list}='.split())

    def test_multiple_lists_fails(self):
        self._verify_invalid(['@{v1}', '@{v2}'])
        self._verify_invalid(['${v1}', '@{v2}', '@{v3}'])

    def test_dict_with_others_fails(self):
        self._verify_invalid(['&{v1}', '&{v2}'])
        self._verify_invalid(['${v1}', '&{v2}'])

    def test_equal_sign_in_wrong_place(self):
        self._verify_invalid(['${v1}=','${v2}'])
        self._verify_invalid(['${v1} =','@{v2} ='])

    def _verify_valid(self, assign):
        assignment = VariableAssignment(assign)
        assignment.validate_assignment()
        expected = [a.rstrip('= ') for a in assign]
        assert_equal(assignment.assignment, expected)

    def _verify_invalid(self, assign):
        assert_raises(DataError, VariableAssignment(assign).validate_assignment)


if __name__ == '__main__':
    unittest.main()
