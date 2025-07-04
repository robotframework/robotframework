import unittest
from decimal import Decimal
from io import StringIO

from robot.utils import JsonLoader
from robot.utils.asserts import assert_equal, assert_raises_with_msg, assert_true


class TestJsonLoader(unittest.TestCase):
    data = '{"x": 1.1, "y": [1, 2], "x": 2.2, "y": [3]}'

    def test_general_config(self):
        x = JsonLoader(parse_float=Decimal).load(self.data)["x"]
        assert_true(isinstance(x, Decimal))
        assert_equal(x, Decimal("2.2"))

    def test_merge_duplicate_lists(self):
        data = JsonLoader().load(self.data)
        assert_equal(data["x"], 2.2)
        assert_equal(data["y"], [1, 2, 3])

    def test_object_hook(self):
        def hook(obj):
            return {**obj, "x": 3.3, "z": "new item"}

        data = JsonLoader(object_hook=hook).load(self.data)
        assert_equal(data["x"], 3.3)
        assert_equal(data["y"], [1, 2, 3])
        assert_equal(data["z"], "new item")
        data = JsonLoader(object_hook=None).load(self.data)
        assert_equal(data["x"], 2.2)
        assert_equal(data["y"], [1, 2, 3])

    def test_object_pairs_hook_cannot_be_set(self):
        assert_raises_with_msg(
            ValueError,
            "'object_pairs_hook' is not supported.",
            JsonLoader,
            object_pairs_hook=dict,
        )
        data = JsonLoader(object_pairs_hook=None).load(self.data)
        assert_equal(data["x"], 2.2)
        assert_equal(data["y"], [1, 2, 3])

    def test_top_level_item_must_be_dictionary(self):
        assert_raises_with_msg(
            TypeError,
            "Expected dictionary, got integer.",
            JsonLoader().load,
            StringIO("42"),
        )


if __name__ == "__main__":
    unittest.main()
