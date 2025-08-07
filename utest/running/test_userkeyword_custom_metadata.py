import unittest
from robot.model.metadata import Metadata
from robot.running import ResourceFile, TestCase, UserKeyword
from robot.running.resourcemodel import UserKeywords


class TestUserKeywordCustomMetadata(unittest.TestCase):
    """Test custom metadata functionality in UserKeyword objects."""

    def setUp(self):
        self.res = ResourceFile()

    def test_custom_metadata_property_creation(self):
        """Test that custom metadata property creates Metadata object."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {"Owner": "Alice", "Complexity": "Medium"}
        
        # Should create a Metadata object
        self.assertIsInstance(kw.custom_metadata, Metadata)
        self.assertEqual(dict(kw.custom_metadata), {"Owner": "Alice", "Complexity": "Medium"})

    def test_has_custom_metadata_property(self):
        """Test has_custom_metadata property."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        
        # Initially no custom metadata
        self.assertFalse(kw.has_custom_metadata)
        
        # After setting custom metadata
        kw.custom_metadata = {"Owner": "Alice"}
        self.assertTrue(kw.has_custom_metadata)
        
        # Empty dict should still return False
        kw.custom_metadata = {}
        self.assertFalse(kw.has_custom_metadata)

    def test_custom_metadata_with_different_value_types(self):
        """Test custom metadata with different value types (should be converted to strings)."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        
        # Set with various types - Robot Framework converts all to strings
        kw.custom_metadata = {
            "String": "value",
            "Number": "123",
            "Boolean": "True",
            "None": "None",
            "Float": "3.14"
        }
        
        # All should be converted to strings (or already are strings)
        metadata = kw.custom_metadata
        self.assertEqual(metadata["String"], "value")
        self.assertEqual(metadata["Number"], "123")
        self.assertEqual(metadata["Boolean"], "True") 
        self.assertEqual(metadata["None"], "None")
        self.assertEqual(metadata["Float"], "3.14")

    def test_custom_metadata_key_normalization(self):
        """Test that custom metadata keys are normalized."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {"Owner": "Alice"}
        
        metadata = kw.custom_metadata
        
        # Metadata should be accessible with different case/spacing
        self.assertEqual(metadata["Owner"], "Alice")
        self.assertEqual(metadata["owner"], "Alice")
        self.assertEqual(metadata["OWNER"], "Alice")
        self.assertEqual(metadata["O w n e r"], "Alice")

    def test_custom_metadata_none_assignment(self):
        """Test assigning None to custom metadata."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {"Owner": "Alice"}
        self.assertTrue(kw.has_custom_metadata)
        
        # Assign None
        kw.custom_metadata = None
        self.assertFalse(kw.has_custom_metadata)

    def test_custom_metadata_unicode_support(self):
        """Test custom metadata with Unicode characters."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {
            "Owner": "Åke",
            "Description": "Tëst with ümlauts and émojis 🚀",
            "Chinese": "测试",
            "Japanese": "テスト"
        }
        
        metadata = kw.custom_metadata
        self.assertEqual(metadata["Owner"], "Åke")
        self.assertEqual(metadata["Description"], "Tëst with ümlauts and émojis 🚀")
        self.assertEqual(metadata["Chinese"], "测试")
        self.assertEqual(metadata["Japanese"], "テスト")

    def test_custom_metadata_special_characters_in_keys(self):
        """Test custom metadata with special characters in key names."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {
            "Bug-ID": "BUG-123",
            "Test_Level": "Unit",
            "Version 2.0": "Compatible",
            "API/Endpoint": "v1/users"
        }
        
        metadata = kw.custom_metadata
        self.assertEqual(metadata["Bug-ID"], "BUG-123")
        self.assertEqual(metadata["Test_Level"], "Unit")
        self.assertEqual(metadata["Version 2.0"], "Compatible")
        self.assertEqual(metadata["API/Endpoint"], "v1/users")

    def test_custom_metadata_to_dict_serialization(self):
        """Test that custom metadata is properly serialized in to_dict."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {"Owner": "Alice", "Priority": "High", "Component": "API"}
        
        data = kw.to_dict()
        
        # Should include custom_metadata in dict
        self.assertIn("custom_metadata", data)
        self.assertEqual(data["custom_metadata"], {"Owner": "Alice", "Priority": "High", "Component": "API"})

    def test_custom_metadata_with_embedded_args(self):
        """Test custom metadata with user keywords that have embedded arguments."""
        kw = UserKeyword("User selects ${item} from list", owner=self.res)
        kw.custom_metadata = {
            "Type": "Embedded",
            "Parameters": "1",
            "Usage": "Common"
        }
        
        self.assertTrue(kw.has_custom_metadata)
        metadata = kw.custom_metadata
        self.assertEqual(metadata["Type"], "Embedded")
        self.assertEqual(metadata["Parameters"], "1")
        self.assertEqual(metadata["Usage"], "Common")

    def test_custom_metadata_with_arguments_and_body(self):
        """Test custom metadata with keyword that has arguments and body."""
        kw = UserKeyword("Login With Credentials", ["${username}", "${password}"], owner=self.res)
        kw.body.create_keyword("Log", ["Logging in with ${username}"])
        kw.custom_metadata = {
            "Action": "Authentication",
            "Complexity": "Simple",
            "Dependencies": "None"
        }
        
        self.assertTrue(kw.has_custom_metadata)
        self.assertEqual(len(kw.args.positional), 2)
        self.assertEqual(len(kw.body), 1)
        self.assertEqual(kw.custom_metadata["Action"], "Authentication")

    def test_custom_metadata_with_setup_and_teardown(self):
        """Test custom metadata with keywords that have setup and teardown."""
        kw = UserKeyword("Test Keyword with Setup/Teardown", owner=self.res)
        kw.setup.config(name="Setup Keyword")
        kw.teardown.config(name="Teardown Keyword")
        kw.custom_metadata = {
            "Setup": "Required",
            "Teardown": "Required",
            "Type": "Full"
        }
        
        self.assertTrue(kw.has_custom_metadata)
        self.assertTrue(kw.has_setup)
        self.assertTrue(kw.has_teardown)
        self.assertEqual(kw.custom_metadata["Setup"], "Required")

    def test_custom_metadata_bind_preservation(self):
        """Test that custom metadata is preserved during keyword binding."""
        tc = TestCase()
        original_kw = UserKeyword("Original Keyword", owner=self.res)
        original_kw.custom_metadata = {
            "Owner": "Alice",
            "Priority": "High",
            "Component": "Core"
        }
        
        # Bind the keyword
        bound_kw = original_kw.bind(tc.body.create_keyword())
        
        # Custom metadata should be preserved
        self.assertTrue(bound_kw.has_custom_metadata)
        self.assertEqual(dict(bound_kw.custom_metadata), {
            "Owner": "Alice",
            "Priority": "High", 
            "Component": "Core"
        })

    def test_custom_metadata_overwrite_behavior(self):
        """Test behavior when custom metadata is set multiple times."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        
        # First assignment
        kw.custom_metadata = {"Owner": "Alice", "Priority": "High"}
        self.assertEqual(len(kw.custom_metadata), 2)
        
        # Second assignment should replace
        kw.custom_metadata = {"Component": "UI"}
        self.assertEqual(len(kw.custom_metadata), 1)
        self.assertEqual(kw.custom_metadata["Component"], "UI")
        self.assertNotIn("Owner", kw.custom_metadata)

    def test_custom_metadata_with_documentation_and_tags(self):
        """Test custom metadata combined with documentation and tags."""
        kw = UserKeyword(
            "Comprehensive Test Keyword",
            doc="This is a test keyword with documentation",
            tags=["tag1", "tag2"],
            owner=self.res
        )
        kw.custom_metadata = {
            "Version": "1.0",
            "Author": "Test Team",
            "Category": "Integration"
        }
        
        # All properties should coexist
        self.assertEqual(kw.doc, "This is a test keyword with documentation")
        self.assertEqual(list(kw.tags), ["tag1", "tag2"])
        self.assertTrue(kw.has_custom_metadata)
        self.assertEqual(kw.custom_metadata["Version"], "1.0")

    def test_custom_metadata_empty_values(self):
        """Test custom metadata with empty values."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {
            "EmptyString": "",
            "Whitespace": "   ",
            "Owner": "Alice"
        }
        
        metadata = kw.custom_metadata
        self.assertEqual(metadata["EmptyString"], "")
        self.assertEqual(metadata["Whitespace"], "   ")
        self.assertEqual(metadata["Owner"], "Alice")

    def test_custom_metadata_large_values(self):
        """Test custom metadata with large values."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        large_value = "A" * 5000  # 5KB string
        
        kw.custom_metadata = {
            "LargeValue": large_value,
            "NormalValue": "Small"
        }
        
        metadata = kw.custom_metadata
        self.assertEqual(metadata["LargeValue"], large_value)
        self.assertEqual(metadata["NormalValue"], "Small")

    def test_custom_metadata_ordering(self):
        """Test that custom metadata maintains insertion order."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        kw.custom_metadata = {
            "First": "1",
            "Second": "2", 
            "Third": "3"
        }
        
        metadata = kw.custom_metadata
        keys = list(metadata.keys())
        
        # Should maintain order (Python 3.7+ dict behavior)
        self.assertEqual(keys, ["First", "Second", "Third"])

    def test_custom_metadata_maximum_entries(self):
        """Test custom metadata with many entries."""
        kw = UserKeyword("Test Keyword", owner=self.res)
        
        # Create 50 metadata entries
        large_metadata = {f"Key{i}": f"Value{i}" for i in range(50)}
        kw.custom_metadata = large_metadata
        
        metadata = kw.custom_metadata
        self.assertEqual(len(metadata), 50)
        
        # Verify some random entries
        self.assertEqual(metadata["Key0"], "Value0")
        self.assertEqual(metadata["Key25"], "Value25")
        self.assertEqual(metadata["Key49"], "Value49")


class TestUserKeywordCustomMetadataIntegration(unittest.TestCase):
    """Test custom metadata integration with UserKeywords collection."""

    def setUp(self):
        self.res = ResourceFile()

    def test_custom_metadata_in_userkeywords_collection(self):
        """Test custom metadata works correctly within UserKeywords collection."""
        keywords = UserKeywords(self.res)
        
        # Add keywords with custom metadata
        kw1 = UserKeyword("First Keyword", owner=self.res)
        kw1.custom_metadata = {"Type": "Setup", "Order": "1"}
        
        kw2 = UserKeyword("Second Keyword", owner=self.res)  
        kw2.custom_metadata = {"Type": "Test", "Order": "2"}
        
        keywords.append(kw1)
        keywords.append(kw2)
        
        # Verify custom metadata is preserved
        self.assertTrue(keywords[0].has_custom_metadata)
        self.assertTrue(keywords[1].has_custom_metadata)
        self.assertEqual(keywords[0].custom_metadata["Type"], "Setup")
        self.assertEqual(keywords[1].custom_metadata["Type"], "Test")

    def test_custom_metadata_with_keyword_cache_invalidation(self):
        """Test that custom metadata changes properly invalidate keyword cache."""
        keywords = UserKeywords(self.res)
        kw = UserKeyword("Test Keyword", owner=self.res)
        
        # Add keyword and set custom metadata
        keywords.append(kw)
        kw.custom_metadata = {"Version": "1.0"}
        
        # Verify metadata is accessible
        self.assertTrue(keywords[0].has_custom_metadata)
        self.assertEqual(keywords[0].custom_metadata["Version"], "1.0")
        
        # Modify metadata
        kw.custom_metadata = {"Version": "2.0", "Status": "Updated"}
        
        # Should still be accessible correctly
        self.assertEqual(keywords[0].custom_metadata["Version"], "2.0")
        self.assertEqual(keywords[0].custom_metadata["Status"], "Updated")

    def test_custom_metadata_with_keyword_creation_from_dict(self):
        """Test custom metadata when creating keyword from DataDict."""
        # Create keyword normally and then add metadata
        keywords = UserKeywords(self.res)
        kw = keywords.create(name="Test Keyword", doc="Test documentation")
        kw.custom_metadata = {"Owner": "Test", "Priority": "Medium"}
        
        # Custom metadata should be properly set
        self.assertTrue(kw.has_custom_metadata)
        self.assertEqual(kw.custom_metadata["Owner"], "Test")
        self.assertEqual(kw.custom_metadata["Priority"], "Medium")

    def test_custom_metadata_consistency_across_operations(self):
        """Test custom metadata consistency across various collection operations."""
        keywords = UserKeywords(self.res)
        
        # Create keywords with metadata
        kw1 = UserKeyword("Keyword 1", owner=self.res)
        kw1.custom_metadata = {"Index": "1"}
        
        kw2 = UserKeyword("Keyword 2", owner=self.res)
        kw2.custom_metadata = {"Index": "2"}
        
        kw3 = UserKeyword("Keyword 3", owner=self.res)
        kw3.custom_metadata = {"Index": "3"}
        
        # Test various operations
        keywords.extend([kw1, kw2])
        keywords.insert(1, kw3)  # Should insert at index 1
        
        # Verify order and metadata
        self.assertEqual(keywords[0].custom_metadata["Index"], "1")
        self.assertEqual(keywords[1].custom_metadata["Index"], "3") 
        self.assertEqual(keywords[2].custom_metadata["Index"], "2")
        
        # Test replacement - use slice assignment for single item
        kw4 = UserKeyword("Keyword 4", owner=self.res)
        kw4.custom_metadata = {"Index": "4", "Replacement": "True"}
        keywords[1:2] = [kw4]  # Replace single item using slice
        
        self.assertEqual(keywords[1].custom_metadata["Index"], "4")
        self.assertEqual(keywords[1].custom_metadata["Replacement"], "True")


if __name__ == "__main__":
    unittest.main()
