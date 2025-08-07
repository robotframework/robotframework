import unittest
from robot.model.metadata import Metadata
from robot.model.testcase import TestCase
from robot.model.testsuite import TestSuite
from robot.utils.asserts import (
    assert_equal, assert_false, assert_not_equal, assert_raises, assert_true
)


class TestTestCaseCustomMetadata(unittest.TestCase):
    """Test custom metadata functionality in TestCase model."""

    def setUp(self):
        self.test = TestCase(name="Test Case")

    def test_has_custom_metadata_initially_false(self):
        """Test that test case initially has no custom metadata."""
        assert_false(self.test.has_custom_metadata)
        assert_equal(self.test.custom_metadata, {})

    def test_set_custom_metadata_from_dict(self):
        """Test setting custom metadata from dictionary."""
        metadata = {"Owner": "Alice", "Priority": "High"}
        self.test.custom_metadata = metadata
        
        assert_true(self.test.has_custom_metadata)
        assert_equal(dict(self.test.custom_metadata), metadata)
        assert_equal(self.test.custom_metadata["Owner"], "Alice")
        assert_equal(self.test.custom_metadata["Priority"], "High")

    def test_set_custom_metadata_from_list_of_tuples(self):
        """Test setting custom metadata from list of tuples."""
        metadata = [("Component", "UI"), ("Team", "Frontend")]
        self.test.custom_metadata = metadata
        
        assert_true(self.test.has_custom_metadata)
        assert_equal(dict(self.test.custom_metadata), {"Component": "UI", "Team": "Frontend"})

    def test_set_custom_metadata_to_none(self):
        """Test setting custom metadata to None."""
        self.test.custom_metadata = {"Owner": "Alice"}
        assert_true(self.test.has_custom_metadata)
        
        self.test.custom_metadata = None
        assert_false(self.test.has_custom_metadata)
        assert_equal(dict(self.test.custom_metadata), {})

    def test_custom_metadata_is_metadata_object(self):
        """Test that custom_metadata property returns Metadata object."""
        self.test.custom_metadata = {"Owner": "Bob"}
        assert_true(isinstance(self.test.custom_metadata, Metadata))

    def test_custom_metadata_normalization(self):
        """Test that custom metadata keys are normalized like regular metadata."""
        self.test.custom_metadata = {
            "Owner": "Alice",
            "OWNER": "Bob",  # Should overwrite first
            "owner": "Charlie",  # Should overwrite again
            "Own_er": "David",  # Should overwrite again
            "Priority": "High"
        }
        
        # Metadata normalizes keys (case, space, underscore insensitive)
        result = dict(self.test.custom_metadata)
        # The last assignment wins due to normalization
        assert_equal(result["Owner"], "David")
        assert_equal(result["Priority"], "High")
        assert_equal(len(result), 2)

    def test_custom_metadata_string_conversion(self):
        """Test that non-string values are converted to strings."""
        self.test.custom_metadata = {
            "Number": 42,
            "Boolean": True,
            "List": [1, 2, 3],
            "None": None
        }
        
        metadata = self.test.custom_metadata
        assert_equal(metadata["Number"], "42")
        assert_equal(metadata["Boolean"], "True")
        assert_equal(metadata["List"], "[1, 2, 3]")
        assert_equal(metadata["None"], "None")

    def test_custom_metadata_modification(self):
        """Test modifying custom metadata after setting."""
        self.test.custom_metadata = {"Owner": "Alice"}
        
        # Modify through the metadata object
        self.test.custom_metadata["Priority"] = "High"
        self.test.custom_metadata["Owner"] = "Bob"
        
        assert_equal(self.test.custom_metadata["Owner"], "Bob")
        assert_equal(self.test.custom_metadata["Priority"], "High")
        assert_equal(len(self.test.custom_metadata), 2)

    def test_custom_metadata_to_dict(self):
        """Test that custom metadata is included in to_dict() output."""
        self.test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        
        test_dict = self.test.to_dict()
        
        assert_true("custom_metadata" in test_dict)
        assert_equal(test_dict["custom_metadata"], {"Owner": "Alice", "Priority": "High"})

    def test_custom_metadata_to_dict_when_empty(self):
        """Test that custom_metadata is not included in to_dict() when empty."""
        test_dict = self.test.to_dict()
        assert_false("custom_metadata" in test_dict)

    def test_custom_metadata_json_serialization(self):
        """Test that custom metadata can be serialized to JSON."""
        self.test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        
        # This should not raise an exception
        json_str = self.test.to_json()
        assert_true('"custom_metadata"' in json_str)
        assert_true('"Owner"' in json_str)
        assert_true('"Alice"' in json_str)

    def test_custom_metadata_copy(self):
        """Test that custom metadata is preserved during copy operations."""
        self.test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        
        # Shallow copy
        copy_test = self.test.copy()
        assert_equal(dict(copy_test.custom_metadata), dict(self.test.custom_metadata))
        
        # Verify they share the same metadata object (shallow copy)
        assert_equal(id(copy_test.custom_metadata), id(self.test.custom_metadata))

    def test_custom_metadata_deepcopy(self):
        """Test that custom metadata is properly deep copied."""
        self.test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        
        # Deep copy
        deep_copy_test = self.test.deepcopy()
        assert_equal(dict(deep_copy_test.custom_metadata), dict(self.test.custom_metadata))
        
        # Verify they have different metadata objects (deep copy)
        assert_not_equal(id(deep_copy_test.custom_metadata), id(self.test.custom_metadata))
        
        # Modify original and verify copy is unaffected
        self.test.custom_metadata["NewKey"] = "NewValue"
        assert_false("NewKey" in deep_copy_test.custom_metadata)

    def test_custom_metadata_with_suite_parent(self):
        """Test custom metadata behavior when test has parent suite."""
        suite = TestSuite(name="Test Suite")
        self.test.parent = suite
        self.test.custom_metadata = {"Owner": "Alice"}
        
        assert_true(self.test.has_custom_metadata)
        assert_equal(self.test.custom_metadata["Owner"], "Alice")

    def test_custom_metadata_slots_enforcement(self):
        """Test that __slots__ prevents adding arbitrary attributes."""
        self.test.custom_metadata = {"Owner": "Alice"}
        
        # Should not be able to add arbitrary attributes
        assert_raises(AttributeError, setattr, self.test, "arbitrary_attribute", "value")


class TestCustomMetadataBoundaryValues(unittest.TestCase):
    """Test boundary values and edge cases for custom metadata."""

    def test_empty_custom_metadata_dict(self):
        """Test setting empty dictionary as custom metadata."""
        test = TestCase()
        test.custom_metadata = {}
        
        assert_false(test.has_custom_metadata)
        assert_equal(dict(test.custom_metadata), {})

    def test_empty_custom_metadata_list(self):
        """Test setting empty list as custom metadata."""
        test = TestCase()
        test.custom_metadata = []
        
        assert_false(test.has_custom_metadata)
        assert_equal(dict(test.custom_metadata), {})

    def test_single_character_metadata_key(self):
        """Test custom metadata with single character key."""
        test = TestCase()
        test.custom_metadata = {"A": "value"}
        
        assert_true(test.has_custom_metadata)
        assert_equal(test.custom_metadata["A"], "value")

    def test_very_long_metadata_key(self):
        """Test custom metadata with very long key."""
        test = TestCase()
        long_key = "A" * 1000
        test.custom_metadata = {long_key: "value"}
        
        assert_true(test.has_custom_metadata)
        assert_equal(test.custom_metadata[long_key], "value")

    def test_very_long_metadata_value(self):
        """Test custom metadata with very long value."""
        test = TestCase()
        long_value = "B" * 10000
        test.custom_metadata = {"Key": long_value}
        
        assert_true(test.has_custom_metadata)
        assert_equal(test.custom_metadata["Key"], long_value)

    def test_unicode_metadata_keys_and_values(self):
        """Test custom metadata with Unicode characters."""
        test = TestCase()
        test.custom_metadata = {
            "Prüfer": "Åsa",
            "组件": "用户界面", 
            "🏷️": "📋",
            "Владелец": "Алиса"
        }
        
        assert_true(test.has_custom_metadata)
        assert_equal(test.custom_metadata["Prüfer"], "Åsa")
        assert_equal(test.custom_metadata["组件"], "用户界面")
        assert_equal(test.custom_metadata["🏷️"], "📋")
        assert_equal(test.custom_metadata["Владелец"], "Алиса")

    def test_metadata_with_special_characters(self):
        """Test custom metadata with special characters in keys and values."""
        test = TestCase()
        test.custom_metadata = {
            "Bug-ID": "PROJ-123",
            "Test_Level": "Unit",
            "Version 2.0": "Compatible",
            "Owner/Reviewer": "Alice/Bob",
            "Key@Domain": "value@example.com",
            "Multi\nLine": "Value\nWith\nNewlines"
        }
        
        assert_true(test.has_custom_metadata)
        assert_equal(test.custom_metadata["Bug-ID"], "PROJ-123")
        assert_equal(test.custom_metadata["Test_Level"], "Unit")
        assert_equal(test.custom_metadata["Version 2.0"], "Compatible")
        assert_equal(test.custom_metadata["Owner/Reviewer"], "Alice/Bob")
        assert_equal(test.custom_metadata["Key@Domain"], "value@example.com")
        assert_equal(test.custom_metadata["Multi\nLine"], "Value\nWith\nNewlines")

    def test_maximum_metadata_entries(self):
        """Test with large number of custom metadata entries."""
        test = TestCase()
        # Create 1000 metadata entries
        large_metadata = {f"Key{i}": f"Value{i}" for i in range(1000)}
        test.custom_metadata = large_metadata
        
        assert_true(test.has_custom_metadata)
        assert_equal(len(test.custom_metadata), 1000)
        assert_equal(test.custom_metadata["Key0"], "Value0")
        assert_equal(test.custom_metadata["Key999"], "Value999")

    def test_metadata_value_types_conversion(self):
        """Test that various Python types are properly converted to strings."""
        test = TestCase()
        test.custom_metadata = {
            "Integer": 42,
            "Float": 3.14159,
            "Boolean_True": True,
            "Boolean_False": False,
            "None_Value": None,
            "List": [1, "two", 3.0],
            "Dict": {"nested": "value"},
            "Tuple": (1, 2, 3),
            "Set": {1, 2, 3}  # Note: sets are unordered
        }
        
        metadata = test.custom_metadata
        assert_equal(metadata["Integer"], "42")
        assert_equal(metadata["Float"], "3.14159")
        assert_equal(metadata["Boolean_True"], "True")
        assert_equal(metadata["Boolean_False"], "False")
        assert_equal(metadata["None_Value"], "None")
        assert_equal(metadata["List"], "[1, 'two', 3.0]")
        assert_equal(metadata["Dict"], "{'nested': 'value'}")
        assert_equal(metadata["Tuple"], "(1, 2, 3)")
        # Set representation might vary, so just check it's a string
        assert_true(isinstance(metadata["Set"], str))
        assert_true("1" in metadata["Set"])

    def test_metadata_key_normalization_edge_cases(self):
        """Test key normalization with edge cases."""
        test = TestCase()
        test.custom_metadata = {
            "Key": "original",
            "KEY": "uppercase",
            "key": "lowercase", 
            "Key_": "underscore",
            "Key ": "space",
            "K e y": "spaced",
            "K_E_Y": "underscored"
        }
        
        # Due to normalization, all these should map to the same key
        # The last one set should win
        metadata = dict(test.custom_metadata)
        assert_equal(len(metadata), 1)  # All normalized to same key
        assert_true("Key" in metadata or "key" in metadata)  # One of these exists


class TestCustomMetadataEquivalenceClasses(unittest.TestCase):
    """Test equivalence classes for custom metadata functionality."""

    def test_valid_metadata_formats(self):
        """Test various valid input formats (equivalence class: valid inputs)."""
        test = TestCase()
        
        # Valid format 1: Dictionary
        test.custom_metadata = {"Owner": "Alice"}
        assert_true(test.has_custom_metadata)
        
        # Valid format 2: List of tuples
        test.custom_metadata = [("Owner", "Bob"), ("Priority", "High")]
        assert_equal(dict(test.custom_metadata), {"Owner": "Bob", "Priority": "High"})
        
        # Valid format 3: Metadata object
        metadata_obj = Metadata({"Component": "UI"})
        test.custom_metadata = metadata_obj
        assert_equal(test.custom_metadata["Component"], "UI")

    def test_empty_or_none_metadata(self):
        """Test empty/None metadata (equivalence class: empty inputs)."""
        test = TestCase()
        
        # None
        test.custom_metadata = None
        assert_false(test.has_custom_metadata)
        
        # Empty dict
        test.custom_metadata = {}
        assert_false(test.has_custom_metadata)
        
        # Empty list
        test.custom_metadata = []
        assert_false(test.has_custom_metadata)

    def test_string_vs_non_string_keys(self):
        """Test string vs non-string keys (equivalence classes)."""
        test = TestCase()
        
        # String keys (valid)
        test.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        assert_equal(test.custom_metadata["Owner"], "Alice")
        
        # Non-string keys (should be converted)
        test.custom_metadata = {123: "number", True: "boolean"}
        assert_equal(test.custom_metadata["123"], "number")
        assert_equal(test.custom_metadata["True"], "boolean")

    def test_string_vs_non_string_values(self):
        """Test string vs non-string values (equivalence classes)."""
        test = TestCase()
        
        # String values
        test.custom_metadata = {"Key1": "string_value"}
        assert_equal(test.custom_metadata["Key1"], "string_value")
        
        # Non-string values (should be converted)
        test.custom_metadata = {"Key2": 42}
        assert_equal(test.custom_metadata["Key2"], "42")


if __name__ == "__main__":
    unittest.main()
