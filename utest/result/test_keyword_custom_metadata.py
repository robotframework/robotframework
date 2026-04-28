import unittest

from robot.model.metadata import Metadata
from robot.result.model import Keyword as ResultKeyword


class TestResultKeywordCustomMetadata(unittest.TestCase):
    """Test custom metadata functionality in result model Keywords."""

    def test_result_keyword_custom_metadata_property(self):
        """Test custom metadata property in result Keyword."""
        kw = ResultKeyword("Test Result Keyword")
        # Use sequence of tuples format for result model
        kw.custom_metadata = [("Owner", "ResultTeam"), ("Status", "Executed")]

        # Should create a Metadata object
        self.assertIsInstance(kw.custom_metadata, Metadata)
        self.assertEqual(
            dict(kw.custom_metadata), {"Owner": "ResultTeam", "Status": "Executed"}
        )

    def test_result_keyword_has_custom_metadata(self):
        """Test has_custom_metadata property in result Keywords."""
        kw = ResultKeyword("Test Keyword")

        # Initially no custom metadata
        self.assertFalse(hasattr(kw, "_setter__custom_metadata"))

        # After setting custom metadata
        kw.custom_metadata = [("Owner", "Alice")]
        self.assertTrue(hasattr(kw, "_setter__custom_metadata"))
        self.assertTrue(bool(getattr(kw, "_setter__custom_metadata", None)))

    def test_result_keyword_custom_metadata_to_dict(self):
        """Test that custom metadata is included in to_dict serialization."""
        kw = ResultKeyword("Serialization Test")
        kw.custom_metadata = [("Component", "Results"), ("Type", "Library")]

        data = kw.to_dict()

        # Should include custom_metadata in dict
        self.assertIn("custom_metadata", data)
        self.assertEqual(
            data["custom_metadata"], {"Component": "Results", "Type": "Library"}
        )

    def test_result_keyword_custom_metadata_normalization(self):
        """Test that custom metadata keys are normalized in result Keywords."""
        kw = ResultKeyword("Normalization Test")
        kw.custom_metadata = [("Owner", "Alice"), ("PRIORITY", "High")]

        metadata = kw.custom_metadata

        # Should be able to access with different cases
        self.assertEqual(metadata["Owner"], "Alice")
        self.assertEqual(metadata["owner"], "Alice")
        self.assertEqual(metadata["PRIORITY"], "High")
        self.assertEqual(metadata["priority"], "High")

    def test_result_keyword_custom_metadata_with_status_data(self):
        """Test custom metadata combined with result status information."""
        kw = ResultKeyword("Status Test", status="PASS")
        kw.message = "Test completed successfully"
        kw.custom_metadata = [
            ("Execution-Time", "0.5s"),
            ("Memory-Usage", "Low"),
            ("Warnings", "None"),
        ]

        # All data should coexist
        self.assertEqual(kw.status, "PASS")
        self.assertEqual(kw.message, "Test completed successfully")
        self.assertTrue(bool(getattr(kw, "_setter__custom_metadata", None)))
        self.assertEqual(kw.custom_metadata["Execution-Time"], "0.5s")

    def test_result_keyword_metadata_compatibility_property(self):
        """Test metadata compatibility property that maps to custom_metadata."""
        kw = ResultKeyword("Compatibility Test")

        # Set via custom_metadata using Metadata object directly
        kw.custom_metadata = Metadata([("Tool", "Robot Framework"), ("Version", "7.0")])

        # Access via metadata property (compatibility)
        metadata_via_compat = kw.metadata
        self.assertIsInstance(metadata_via_compat, Metadata)
        self.assertEqual(metadata_via_compat["Tool"], "Robot Framework")
        self.assertEqual(metadata_via_compat["Version"], "7.0")

    def test_result_keyword_custom_metadata_with_nested_keywords(self):
        """Test custom metadata with nested keywords in body."""
        parent_kw = ResultKeyword("Parent Keyword")
        parent_kw.custom_metadata = [("Type", "Parent"), ("Level", "1")]

        # Add nested keyword to body
        nested_kw = parent_kw.body.create_keyword("Nested Keyword")
        nested_kw.custom_metadata = [("Type", "Nested"), ("Level", "2")]

        # Both should maintain their custom metadata
        self.assertEqual(parent_kw.custom_metadata["Type"], "Parent")
        self.assertEqual(nested_kw.custom_metadata["Type"], "Nested")
        self.assertEqual(parent_kw.custom_metadata["Level"], "1")
        self.assertEqual(nested_kw.custom_metadata["Level"], "2")

    def test_result_keyword_custom_metadata_unicode_and_special_chars(self):
        """Test result keyword custom metadata with Unicode and special characters."""
        kw = ResultKeyword("Unicode Test")
        kw.custom_metadata = [
            ("Тест", "Значение"),  # Cyrillic
            ("測試", "価値"),  # Chinese/Japanese
            ("emoji-key", "🚀🎯✅"),
            ("special-chars", "!@#$%^&*()"),
        ]

        metadata = kw.custom_metadata
        self.assertEqual(metadata["Тест"], "Значение")
        self.assertEqual(metadata["測試"], "価値")
        self.assertEqual(metadata["emoji-key"], "🚀🎯✅")
        self.assertEqual(metadata["special-chars"], "!@#$%^&*()")

    def test_result_keyword_custom_metadata_empty_and_none_values(self):
        """Test result keyword custom metadata with empty and None values."""
        kw = ResultKeyword("Empty Values Test")

        # Test with empty list - should create empty metadata
        kw.custom_metadata = []
        self.assertFalse(bool(getattr(kw, "_setter__custom_metadata", None)))

        # Test with actual values including empty strings
        kw.custom_metadata = [("Empty", ""), ("Spaces", "   "), ("Valid", "Value")]
        metadata = kw.custom_metadata
        self.assertEqual(metadata["Empty"], "")
        self.assertEqual(metadata["Spaces"], "   ")
        self.assertEqual(metadata["Valid"], "Value")

    def test_result_keyword_custom_metadata_large_dataset(self):
        """Test result keyword custom metadata with large number of entries."""
        kw = ResultKeyword("Large Dataset Test")

        # Create 100 metadata entries as tuples
        large_metadata = [(f"Field{i}", f"Data{i}") for i in range(100)]
        kw.custom_metadata = large_metadata

        # Verify all entries are accessible
        metadata = kw.custom_metadata
        self.assertEqual(len(metadata), 100)
        self.assertEqual(metadata["Field0"], "Data0")
        self.assertEqual(metadata["Field50"], "Data50")
        self.assertEqual(metadata["Field99"], "Data99")

    def test_result_keyword_custom_metadata_overwrite_scenarios(self):
        """Test various overwrite scenarios with result keyword custom metadata."""
        kw = ResultKeyword("Overwrite Test")

        # Initial assignment
        kw.custom_metadata = [("Version", "1.0"), ("Status", "Initial")]

        # Partial overwrite via new assignment
        kw.custom_metadata = [
            ("Version", "2.0"),
            ("Status", "Updated"),
            ("New", "Field"),
        ]

        # Should completely replace previous metadata
        self.assertEqual(len(kw.custom_metadata), 3)
        self.assertEqual(kw.custom_metadata["Version"], "2.0")
        self.assertEqual(kw.custom_metadata["Status"], "Updated")
        self.assertEqual(kw.custom_metadata["New"], "Field")

    def test_result_keyword_custom_metadata_with_execution_context(self):
        """Test custom metadata in context of executed keyword results."""
        kw = ResultKeyword("Execution Context Test", status="PASS")
        kw.start_time = "2023-01-01T00:00:00"
        kw.end_time = "2023-01-01T00:00:01"
        kw.elapsed_time = 1.0

        # Add execution-related custom metadata
        kw.custom_metadata = [
            ("Execution-Environment", "CI/CD"),
            ("Test-Run-ID", "12345"),
            ("Browser", "Chrome"),
            ("Platform", "Linux"),
            ("Performance-Baseline", "1.2s"),
        ]

        # All execution context should be preserved
        self.assertEqual(kw.status, "PASS")
        # elapsed_time is a timedelta, not float
        self.assertEqual(kw.elapsed_time.total_seconds(), 1.0)
        self.assertEqual(kw.custom_metadata["Execution-Environment"], "CI/CD")
        self.assertEqual(kw.custom_metadata["Test-Run-ID"], "12345")
        self.assertEqual(kw.custom_metadata["Performance-Baseline"], "1.2s")

    def test_result_keyword_custom_metadata_with_metadata_object(self):
        """Test setting custom metadata using Metadata object directly."""
        kw = ResultKeyword("Metadata Object Test")

        # Create Metadata object first
        metadata_obj = Metadata([("Direct", "Assignment"), ("Object", "Based")])
        kw.custom_metadata = metadata_obj

        # Should preserve the metadata
        self.assertEqual(kw.custom_metadata["Direct"], "Assignment")
        self.assertEqual(kw.custom_metadata["Object"], "Based")
        self.assertEqual(len(kw.custom_metadata), 2)


if __name__ == "__main__":
    unittest.main()
