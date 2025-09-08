import unittest

from robot.model.metadata import Metadata
from robot.model.testcase import TestCase
from robot.utils.asserts import assert_equal, assert_false, assert_true


class TestCustomMetadataModel(unittest.TestCase):
    """Test custom metadata in TestCase model objects."""

    def test_custom_metadata_property_and_has_metadata(self):
        """Test custom metadata property creation and has_custom_metadata property."""
        test = TestCase("Test with metadata")

        # Initially no custom metadata
        assert_false(test.has_custom_metadata)

        # After setting custom metadata
        test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        assert_true(isinstance(test.custom_metadata, Metadata))
        assert_equal(dict(test.custom_metadata), {"Owner": "Alice", "Priority": "High"})
        assert_true(test.has_custom_metadata)

        # Empty dict should return False
        test.custom_metadata = {}
        assert_false(test.has_custom_metadata)

        # None should return False
        test.custom_metadata = None
        assert_false(test.has_custom_metadata)

    def test_custom_metadata_serialization_and_types(self):
        """Test custom metadata serialization to dict/JSON and type conversion."""
        import json

        test = TestCase("Test with metadata")
        test.custom_metadata = {
            "Owner": "Alice",
            "Priority": "High",
            "Component": "UI",
            "Number": "123",
            "Boolean": "True",
            "None": "None",
        }

        # Test to_dict serialization
        data = test.to_dict()
        assert_true("custom_metadata" in data)
        expected_dict = {
            "Owner": "Alice",
            "Priority": "High",
            "Component": "UI",
            "Number": "123",
            "Boolean": "True",
            "None": "None",
        }
        assert_equal(data["custom_metadata"], expected_dict)

        # Test JSON serialization
        json_str = test.to_json()
        parsed = json.loads(json_str)
        assert_true("custom_metadata" in parsed)
        assert_equal(parsed["custom_metadata"], expected_dict)

    def test_custom_metadata_key_normalization_and_special_chars(self):
        """Test custom metadata key normalization and special characters."""
        test = TestCase("Test")

        # Test key normalization (case insensitive, space normalization)
        test.custom_metadata = {"Owner": "Alice"}
        metadata = test.custom_metadata
        assert_equal(metadata["Owner"], "Alice")
        assert_equal(metadata["owner"], "Alice")
        assert_equal(metadata["OWNER"], "Alice")
        assert_equal(metadata["O w n e r"], "Alice")

        # Test special characters in keys and values
        test.custom_metadata = {
            "Bug-ID": "BUG-123",
            "Test_Level": "Unit",
            "Version 2.0": "Compatible",
            "Path": "/path/to/resource",
            "Pattern": ".*\\.txt$",
        }

        metadata = test.custom_metadata
        assert_equal(metadata["Bug-ID"], "BUG-123")
        assert_equal(metadata["Test_Level"], "Unit")
        assert_equal(metadata["Version 2.0"], "Compatible")
        assert_equal(metadata["Path"], "/path/to/resource")
        assert_equal(metadata["Pattern"], ".*\\.txt$")

    def test_custom_metadata_unicode_and_large_values(self):
        """Test custom metadata with Unicode and large values."""
        test = TestCase("Test")
        large_value = "A" * 10000  # 10KB string

        test.custom_metadata = {
            "Owner": "Åke",
            "Description": "Tëst with ümlauts and émojis 🚀",
            "Chinese": "测试",
            "Japanese": "テスト",
            "LargeValue": large_value,
            "EmptyString": "",
            "Whitespace": "   ",
        }

        metadata = test.custom_metadata
        assert_equal(metadata["Owner"], "Åke")
        assert_equal(metadata["Description"], "Tëst with ümlauts and émojis 🚀")
        assert_equal(metadata["Chinese"], "测试")
        assert_equal(metadata["Japanese"], "テスト")
        assert_equal(metadata["LargeValue"], large_value)
        assert_equal(metadata["EmptyString"], "")
        assert_equal(metadata["Whitespace"], "   ")

    def test_custom_metadata_ordering_and_overwrite(self):
        """Test custom metadata ordering and overwrite behavior."""
        test = TestCase("Test")

        # Test ordering (Python 3.7+ dict behavior)
        test.custom_metadata = {"First": "1", "Second": "2", "Third": "3"}
        keys = list(test.custom_metadata.keys())
        assert_equal(keys, ["First", "Second", "Third"])

        # Test overwrite behavior
        test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        assert_equal(len(test.custom_metadata), 2)

        # Second assignment should replace
        test.custom_metadata = {"Component": "UI"}
        assert_equal(len(test.custom_metadata), 1)
        assert_equal(test.custom_metadata["Component"], "UI")
        assert_false("Owner" in test.custom_metadata)

    def test_custom_metadata_across_model_types(self):
        """Test custom metadata consistency across different model types."""
        from robot.model.testcase import TestCase
        from robot.result.model import TestCase as ResultTestCase
        from robot.running.model import TestCase as RunningTestCase

        # Test with base model TestCase
        base_test = TestCase("Base Test")
        base_test.custom_metadata = {"Type": "Base"}
        assert_true(base_test.has_custom_metadata)
        assert_equal(base_test.custom_metadata["Type"], "Base")

        # Test with running model TestCase
        running_test = RunningTestCase("Running Test")
        running_test.custom_metadata = {"Type": "Running"}
        assert_true(running_test.has_custom_metadata)
        assert_equal(running_test.custom_metadata["Type"], "Running")

        # Test with result model TestCase
        result_test = ResultTestCase("Result Test")
        result_test.custom_metadata = {"Type": "Result"}
        assert_true(result_test.has_custom_metadata)
        assert_equal(result_test.custom_metadata["Type"], "Result")

    def test_custom_metadata_edge_cases_and_maximum_entries(self):
        """Test edge cases and maximum entries for custom metadata."""
        test = TestCase("Test")

        # Test with many entries
        large_metadata = {f"Key{i}": f"Value{i}" for i in range(100)}
        test.custom_metadata = large_metadata

        metadata = test.custom_metadata
        assert_equal(len(metadata), 100)
        assert_equal(metadata["Key0"], "Value0")
        assert_equal(metadata["Key50"], "Value50")
        assert_equal(metadata["Key99"], "Value99")

        # Test has_custom_metadata edge cases with internal state
        test.custom_metadata = {}
        assert_false(test.has_custom_metadata)

        test.custom_metadata = None
        assert_false(test.has_custom_metadata)

        test.custom_metadata = {"Key": "Value"}
        assert_true(test.has_custom_metadata)

        test.custom_metadata = {}  # Empty again after having metadata
        assert_false(test.has_custom_metadata)


if __name__ == "__main__":
    unittest.main()
