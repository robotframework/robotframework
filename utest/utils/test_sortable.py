import unittest
from decimal import Decimal
from fractions import Fraction

from robot.utils import safe_sort_key, Sortable
from robot.utils.asserts import assert_equal, assert_raises, assert_true


class MySortable(Sortable):

    def __init__(self, sort_key=NotImplemented):
        self._sort_key = sort_key


class MyComparable:

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


class TestSortable(unittest.TestCase):

    def setUp(self):
        self.a = MySortable("a")
        self.a2 = MySortable("a")
        self.b = MySortable("b")

    def test_eq(self):
        assert_true(self.a == self.a2)
        assert_true(not self.a == self.b)  # noqa: SIM201
        assert_true(not self.a == 1)  # noqa: SIM201

    def test_ne(self):
        assert_true(self.a != self.b)
        assert_true(not self.a != self.a2)  # noqa: SIM202
        assert_true(self.a != 1)

    def test_lt(self):
        assert_true(self.a < self.b)
        assert_true(not self.a < self.a2)
        assert_raises(TypeError, lambda: self.a < 1)

    def test_gt(self):
        assert_true(self.b > self.a)
        assert_true(not self.a > self.a2)
        assert_raises(TypeError, lambda: self.a > 1)

    def test_le(self):
        assert_true(self.a <= self.a)
        assert_true(self.a <= self.b)
        assert_true(not self.b <= self.a)
        assert_raises(TypeError, lambda: self.a <= 1)

    def test_ge(self):
        assert_true(self.a >= self.a)
        assert_true(self.b >= self.a)
        assert_true(not self.a >= self.b)
        assert_raises(TypeError, lambda: self.a >= 1)


class TestSafeSortKey(unittest.TestCase):

    def test_natively_sortable_values(self):
        for values in (
            [3, 1, 2],
            [1.5, -2, 3],
            [Decimal("2.5"), Decimal("1.5")],
            ["b", "a", "c"],
            [(2, 1), (1, 2)],
            [True, False],
        ):
            assert_equal(sorted(values), sorted(values, key=safe_sort_key))

    def test_mixed_numbers(self):
        values = [3, -2.1, Decimal("2.5"), Fraction(1, 2)]
        assert_equal(sorted(values), sorted(values, key=safe_sort_key))

    def test_complex_numbers(self):
        values = [2 + 1j, 1 + 2j, 1 + 1j]
        assert_equal(
            sorted(values, key=safe_sort_key),
            [1 + 1j, 1 + 2j, 2 + 1j],
        )

    def test_none(self):
        assert_equal(sorted([None, None], key=safe_sort_key), [None, None])

    def test_dictionaries(self):
        values = [{"b": 1}, {"a": 2}, {"a": 1}]
        assert_equal(
            sorted(values, key=safe_sort_key),
            [{"a": 1}, {"a": 2}, {"b": 1}],
        )

    def test_dictionaries_in_different_order(self):
        values = [{"a": 1, "b": 2}, {"a": 1, "b": 1}]
        reversed_values = list(reversed(values))
        assert_equal(
            sorted(values, key=safe_sort_key),
            sorted(reversed_values, key=safe_sort_key),
        )

    def test_nested_unsortable_values(self):
        values = [
            {"a": [{"x": 2}, {"x": 1}]},
            {"a": [{"x": 1}, {"x": 2}]},
        ]
        reversed_values = list(reversed(values))
        assert_equal(
            sorted(values, key=safe_sort_key),
            sorted(reversed_values, key=safe_sort_key),
        )

    def test_mixed_unsortable_and_sortable_values(self):
        values = [None, 1, "a", {"k": 1}, [1, 2], (1, 2), b"a", 1 + 2j]
        reversed_values = list(reversed(values))
        assert_equal(
            sorted(values, key=safe_sort_key),
            sorted(reversed_values, key=safe_sort_key),
        )

    def test_custom_sortable_objects(self):
        values = [MyComparable(2), MyComparable(1)]
        assert_equal(
            [value.value for value in sorted(values, key=safe_sort_key)],
            [1, 2],
        )

    def test_unsortable_objects(self):
        assert_equal(len(sorted([object(), object()], key=safe_sort_key)), 2)


if __name__ == "__main__":
    unittest.main()
