import unittest
from robot.libraries.String import String

class TestStringLibrary(unittest.TestCase):
    def setUp(self):
        self.string_lib = String()

    def test_get_substring_empty_end(self):
        result = self.string_lib.get_substring("foobar", 1, "")
        self.assertEqual(result, "oobar")

    def test_split_to_lines_empty_end(self):
        result = self.string_lib.split_to_lines("foo\nbar\nbaz", 1, "")
        self.assertEqual(result, ["bar", "baz"])

if __name__ == '__main__':
    unittest.main()
