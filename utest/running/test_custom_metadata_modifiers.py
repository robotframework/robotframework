import unittest
from textwrap import dedent
from unittest.mock import Mock

from robot.running import TestSuiteBuilder
from robot.utils.asserts import assert_equal, assert_false, assert_true


class TestCustomMetadataModifiers(unittest.TestCase):
    """Test custom metadata interaction with pre-run modifiers and listeners."""

    def setUp(self):
        """Set up test environment with a sample test suite."""
        self.data = dedent(
            """\
            *** Test Cases ***
            Test With Metadata
                [Owner]           Alice
                [Priority]        High
                [Component]       UI
                Log               Hello World
                
            Test Without Metadata
                Log               No metadata here
                
            Another Test With Metadata
                [Owner]           Bob
                [Environment]     Staging
                [Bug-ID]          BUG-123
                Log               Another test
        """
        )

    def _build_suite(self, **config):
        """Helper to build suite from test data."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".robot", delete=False) as f:
            f.write(self.data)
            temp_file = f.name

        try:
            suite = TestSuiteBuilder(**config).build(temp_file)
            return suite
        finally:
            os.unlink(temp_file)

    def test_modifier_can_access_and_modify_custom_metadata(self):
        """Test that pre-run modifiers can access and modify custom metadata."""
        from robot.api import SuiteVisitor

        class CustomMetadataModifier(SuiteVisitor):
            """Modifier that accesses and changes custom metadata."""

            def __init__(self):
                self.visited_tests = []
                self.metadata_seen = []

            def visit_test(self, test):
                self.visited_tests.append(test.name)

                # Access custom metadata
                if test.has_custom_metadata:
                    metadata = dict(test.custom_metadata)
                    self.metadata_seen.append(metadata)

                    # Modify metadata
                    if "Owner" in metadata:
                        # Change owner value
                        test.custom_metadata["Owner"] = f"Modified_{metadata['Owner']}"

                    # Add new metadata
                    test.custom_metadata["ModifierApplied"] = "True"
                else:
                    self.metadata_seen.append({})
                    # Add metadata to tests without existing metadata
                    test.custom_metadata["ModifierApplied"] = "True"

        suite = self._build_suite()
        modifier = CustomMetadataModifier()

        # Apply modifier
        suite.visit(modifier)

        # Verify modifier accessed metadata correctly
        assert_equal(len(modifier.visited_tests), 3)
        assert_equal(len(modifier.metadata_seen), 3)

        # Check original metadata was seen
        expected_metadata = [
            {"Owner": "Alice", "Priority": "High", "Component": "UI"},
            {},  # No metadata test
            {"Owner": "Bob", "Environment": "Staging", "Bug-ID": "BUG-123"},
        ]
        assert_equal(modifier.metadata_seen, expected_metadata)

        # Verify modifications were applied
        test1 = suite.tests[0]
        assert_equal(test1.custom_metadata["Owner"], "Modified_Alice")
        assert_equal(test1.custom_metadata["ModifierApplied"], "True")
        assert_equal(test1.custom_metadata["Priority"], "High")  # Unchanged

        test2 = suite.tests[1]
        assert_true(test2.has_custom_metadata)  # Now has metadata
        assert_equal(test2.custom_metadata["ModifierApplied"], "True")
        assert_false("Owner" in dict(test2.custom_metadata))

        test3 = suite.tests[2]
        assert_equal(test3.custom_metadata["Owner"], "Modified_Bob")
        assert_equal(test3.custom_metadata["ModifierApplied"], "True")
        assert_equal(test3.custom_metadata["Bug-ID"], "BUG-123")  # Unchanged

    def test_listener_can_access_custom_metadata_during_execution(self):
        """Test that listeners can access custom metadata during test execution."""

        class CustomMetadataListener:
            """Listener that logs custom metadata during execution."""

            def __init__(self):
                self.test_starts = []
                self.metadata_at_start = []

            def start_test(self, data, test):
                self.test_starts.append(test.name)

                if hasattr(test, "custom_metadata") and test.has_custom_metadata:
                    metadata = dict(test.custom_metadata)
                    self.metadata_at_start.append(metadata)
                else:
                    self.metadata_at_start.append({})

        suite = self._build_suite()
        listener = CustomMetadataListener()

        # Simulate execution with listener
        for test in suite.tests:
            listener.start_test(None, test)

        # Verify listener accessed metadata correctly
        assert_equal(len(listener.test_starts), 3)
        assert_equal(len(listener.metadata_at_start), 3)

        expected_metadata = [
            {"Owner": "Alice", "Priority": "High", "Component": "UI"},
            {},
            {"Owner": "Bob", "Environment": "Staging", "Bug-ID": "BUG-123"},
        ]
        assert_equal(listener.metadata_at_start, expected_metadata)

    def test_complex_modifier_filtering_and_transformation(self):
        """Test complex modifier that filters and transforms metadata."""
        from robot.api import SuiteVisitor

        class AdvancedMetadataProcessor(SuiteVisitor):
            """Advanced processor that filters, transforms and adds metadata."""

            def visit_test(self, test):
                if test.has_custom_metadata:
                    metadata = dict(test.custom_metadata)

                    # Remove sensitive metadata
                    if "Bug-ID" in metadata:
                        del test.custom_metadata["Bug-ID"]

                    # Normalize owner names
                    if "Owner" in metadata:
                        test.custom_metadata["Owner"] = metadata["Owner"].upper()

                    # Add derived metadata
                    if "Priority" in metadata:
                        if metadata["Priority"] == "High":
                            test.custom_metadata["Critical"] = "True"
                        else:
                            test.custom_metadata["Critical"] = "False"

                    # Add test metadata
                    test.custom_metadata["ProcessedAt"] = "2023-01-01"
                    test.custom_metadata["ProcessorVersion"] = "1.0"
                else:
                    # Add metadata to tests without existing metadata
                    test.custom_metadata["ProcessedAt"] = "2023-01-01"
                    test.custom_metadata["ProcessorVersion"] = "1.0"

        suite = self._build_suite()
        processor = AdvancedMetadataProcessor()

        # Apply processor
        suite.visit(processor)

        # Verify transformations
        test1 = suite.tests[0]
        test1_metadata = dict(test1.custom_metadata)
        assert_equal(test1_metadata["Owner"], "ALICE")  # Uppercase
        assert_equal(test1_metadata["Priority"], "High")  # Unchanged
        assert_equal(test1_metadata["Critical"], "True")  # Added
        assert_equal(test1_metadata["ProcessedAt"], "2023-01-01")  # Added
        assert_equal(test1_metadata["ProcessorVersion"], "1.0")  # Added
        assert_equal(test1_metadata["Component"], "UI")  # Unchanged

        test2 = suite.tests[1]
        test2_metadata = dict(test2.custom_metadata)
        assert_equal(test2_metadata["ProcessedAt"], "2023-01-01")  # Added
        assert_equal(test2_metadata["ProcessorVersion"], "1.0")  # Added
        assert_equal(len(test2_metadata), 2)  # Only added metadata

        test3 = suite.tests[2]
        test3_metadata = dict(test3.custom_metadata)
        assert_equal(test3_metadata["Owner"], "BOB")  # Uppercase
        assert_equal(test3_metadata["Environment"], "Staging")  # Unchanged
        assert_false("Bug-ID" in test3_metadata)  # Removed
        assert_false("Critical" in test3_metadata)  # Not added (no Priority)
        assert_equal(test3_metadata["ProcessedAt"], "2023-01-01")  # Added
        assert_equal(test3_metadata["ProcessorVersion"], "1.0")  # Added

    def test_modifier_with_filtering_configuration_interaction(self):
        """Test modifier behavior when custom metadata filtering is configured."""
        from robot.api import SuiteVisitor

        class MetadataAnalyzer(SuiteVisitor):
            """Analyzer that examines what metadata is available."""

            def __init__(self):
                self.analysis_results = []

            def visit_test(self, test):
                result = {
                    "test_name": test.name,
                    "has_metadata": test.has_custom_metadata,
                    "metadata_count": (
                        len(dict(test.custom_metadata))
                        if test.has_custom_metadata
                        else 0
                    ),
                    "metadata_keys": (
                        list(test.custom_metadata.keys())
                        if test.has_custom_metadata
                        else []
                    ),
                }
                self.analysis_results.append(result)

        # Test with no filtering
        suite1 = self._build_suite()
        analyzer1 = MetadataAnalyzer()
        suite1.visit(analyzer1)

        # Test with filtering (only Owner and Priority allowed)
        suite2 = self._build_suite(custom_metadata=["Owner", "Priority"])
        analyzer2 = MetadataAnalyzer()
        suite2.visit(analyzer2)

        # Test with empty filtering (no metadata allowed)
        suite3 = self._build_suite(custom_metadata=[])
        analyzer3 = MetadataAnalyzer()
        suite3.visit(analyzer3)

        # Verify no filtering results
        result1 = analyzer1.analysis_results[0]  # First test
        assert_equal(result1["has_metadata"], True)
        assert_equal(result1["metadata_count"], 3)
        assert_equal(set(result1["metadata_keys"]), {"Owner", "Priority", "Component"})

        # Verify filtered results
        result2 = analyzer2.analysis_results[0]  # First test
        assert_equal(result2["has_metadata"], True)
        assert_equal(result2["metadata_count"], 2)
        assert_equal(set(result2["metadata_keys"]), {"Owner", "Priority"})

        # Verify empty filtering results
        result3 = analyzer3.analysis_results[0]  # First test
        assert_equal(result3["has_metadata"], False)
        assert_equal(result3["metadata_count"], 0)
        assert_equal(result3["metadata_keys"], [])

    def test_listener_integration_with_execution_model(self):
        """Test listener integration with the complete execution model."""

        class ComprehensiveListener:
            """Comprehensive listener that tracks metadata throughout execution."""

            def __init__(self):
                self.suite_starts = []
                self.test_starts = []
                self.keyword_starts = []
                self.collected_metadata = {}

            def start_suite(self, data, suite):
                self.suite_starts.append(suite.name)

            def start_test(self, data, test):
                self.test_starts.append(test.name)
                if hasattr(test, "custom_metadata") and test.has_custom_metadata:
                    self.collected_metadata[test.name] = dict(test.custom_metadata)
                else:
                    self.collected_metadata[test.name] = {}

            def start_keyword(self, data, keyword):
                self.keyword_starts.append(keyword.name)

        suite = self._build_suite()
        listener = ComprehensiveListener()

        # Simulate full execution cycle
        listener.start_suite(None, suite)
        for test in suite.tests:
            listener.start_test(None, test)
            # Simulate keywords in test
            listener.start_keyword(None, Mock(name="Log"))

        # Verify listener collected data correctly
        assert_equal(len(listener.suite_starts), 1)
        assert_equal(len(listener.test_starts), 3)
        assert_equal(len(listener.keyword_starts), 3)  # One Log per test

        expected_metadata = {
            "Test With Metadata": {
                "Owner": "Alice",
                "Priority": "High",
                "Component": "UI",
            },
            "Test Without Metadata": {},
            "Another Test With Metadata": {
                "Owner": "Bob",
                "Environment": "Staging",
                "Bug-ID": "BUG-123",
            },
        }
        assert_equal(listener.collected_metadata, expected_metadata)

    def test_modifier_error_handling_and_robustness(self):
        """Test modifier error handling and robustness with various edge cases."""
        from robot.api import SuiteVisitor

        class RobustModifier(SuiteVisitor):
            """Modifier that handles various edge cases gracefully."""

            def __init__(self):
                self.errors_encountered = []
                self.successful_modifications = 0

            def visit_test(self, test):
                try:
                    # Handle tests without metadata
                    if not hasattr(test, "custom_metadata"):
                        self.errors_encountered.append(
                            f"No custom_metadata attr on {test.name}"
                        )
                        return

                    # Handle tests with empty metadata
                    if not test.has_custom_metadata:
                        # Add default metadata
                        test.custom_metadata["DefaultOwner"] = "System"
                        test.custom_metadata["LastModified"] = "2023-01-01T00:00:00"
                        self.successful_modifications += 1
                        return

                    # Handle existing metadata
                    metadata = dict(test.custom_metadata)

                    # Safe operations that don't fail
                    if "Owner" in metadata:
                        # Validate owner format
                        owner = metadata["Owner"]
                        if owner and isinstance(owner, str):
                            test.custom_metadata["Owner"] = owner.strip().title()
                        else:
                            test.custom_metadata["Owner"] = "Unknown"

                    # Add processing timestamp
                    test.custom_metadata["LastModified"] = "2023-01-01T00:00:00"

                    self.successful_modifications += 1

                except Exception as e:
                    self.errors_encountered.append(f"Error processing {test.name}: {e}")

        suite = self._build_suite()
        modifier = RobustModifier()

        # Apply modifier
        suite.visit(modifier)

        # Verify no errors occurred
        assert_equal(len(modifier.errors_encountered), 0)
        assert_equal(modifier.successful_modifications, 3)

        # Verify modifications were applied correctly
        test1 = suite.tests[0]
        assert_equal(test1.custom_metadata["Owner"], "Alice")  # Title case
        assert_equal(test1.custom_metadata["LastModified"], "2023-01-01T00:00:00")

        test2 = suite.tests[1]
        assert_equal(test2.custom_metadata["DefaultOwner"], "System")  # Added default
        assert_equal(test2.custom_metadata["LastModified"], "2023-01-01T00:00:00")

        test3 = suite.tests[2]
        assert_equal(test3.custom_metadata["Owner"], "Bob")  # Title case
        assert_equal(test3.custom_metadata["LastModified"], "2023-01-01T00:00:00")


if __name__ == "__main__":
    unittest.main()
