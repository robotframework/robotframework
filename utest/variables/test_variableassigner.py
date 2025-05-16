import unittest

from robot.errors import DataError
from robot.utils.asserts import assert_equal, assert_raises_with_msg
from robot.variables import VariableAssignment


class TestResolveAssignment(unittest.TestCase):

    def test_one_scalar(self):
        self._verify_valid(["${var}"])

    def test_multiple_scalars(self):
        self._verify_valid("${v1} ${v2} ${v3}".split())

    def test_list(self):
        self._verify_valid(["@{list}"])

    def test_dict(self):
        self._verify_valid(["&{dict}"])

    def test_scalars_and_list(self):
        self._verify_valid("${v1} ${v2} @{list}".split())
        self._verify_valid("@{list} ${v1} ${v2}".split())
        self._verify_valid("${v1} @{list} ${v2}".split())

    def test_equal_sign(self):
        self._verify_valid(["${var} ="])
        self._verify_valid("${v1} ${v2} @{list}=".split())

    def test_multiple_lists_fails(self):
        self._verify_invalid(
            ["@{v1}", "@{v2}"],
            "Assignment can contain only one list variable.",
        )
        self._verify_invalid(
            ["${v1}", "@{v2}", "@{v3}", "${v4}", "@{v5}"],
            "Assignment can contain only one list variable.",
        )

    def test_dict_with_others_fails(self):
        self._verify_invalid(
            ["&{v1}", "&{v2}"],
            "Dictionary variable cannot be assigned with other variables.",
        )
        self._verify_invalid(
            ["${v1}", "&{v2}"],
            "Dictionary variable cannot be assigned with other variables.",
        )

    def test_equal_sign_in_wrong_place(self):
        self._verify_invalid(
            ["${v1}=", "${v2}"],
            "Assign mark '=' can be used only with the last variable.",
        )
        self._verify_invalid(
            ["${v1} =", "@{v2} =", "${v3}"],
            "Assign mark '=' can be used only with the last variable.",
        )

    def test_multiple_errors(self):
        self._verify_invalid(
            ["@{v1}=", "&{v2}=", "@{v3}=", "&{v4}=", "@{v5}="],
            """Multiple errors:
- Assign mark '=' can be used only with the last variable.
- Dictionary variable cannot be assigned with other variables.
- Assignment can contain only one list variable.""",
        )

    def _verify_valid(self, assign):
        assignment = VariableAssignment(assign)
        assignment.validate_assignment()
        expected = [a.rstrip("= ") for a in assign]
        assert_equal(assignment.assignment, expected)

    def _verify_invalid(self, assign, error):
        assert_raises_with_msg(
            DataError,
            error,
            VariableAssignment(assign).validate_assignment,
        )


if __name__ == "__main__":
    unittest.main()
