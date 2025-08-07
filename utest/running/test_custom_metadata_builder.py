import unittest
from textwrap import dedent

from robot.running import TestSuiteBuilder
from robot.utils.asserts import assert_equal, assert_false, assert_true


class TestCustomMetadataBuilder(unittest.TestCase):
    """Test custom metadata functionality in the builder layer."""

    def _build_from_string(self, data, **config):
        """Helper to build suite from string data."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.robot', delete=False) as f:
            f.write(data)
            temp_file = f.name
        
        try:
            suite = TestSuiteBuilder(**config).build(temp_file)
            return suite
        finally:
            os.unlink(temp_file)

    def test_custom_metadata_basic_filtering_behavior(self):
        """Test basic custom metadata filtering with different allowed lists."""
        data = dedent("""\
            *** Test Cases ***
            Test With Custom Metadata
                [Owner]           Alice
                [Priority]        High
                [Component]       UI
                [NotAllowed]      Should be filtered
                Log               Hello
        """)
        
        # Test without filtering (all metadata included)
        suite = self._build_from_string(data)
        test = suite.tests[0]
        assert_true(test.has_custom_metadata)
        metadata = dict(test.custom_metadata)
        assert_equal(metadata, {
            "Owner": "Alice",
            "Priority": "High",
            "Component": "UI", 
            "NotAllowed": "Should be filtered"
        })
        
        # Test with allowed list (only specific metadata included)
        suite = self._build_from_string(data, custom_metadata=["Owner", "Priority"])
        test = suite.tests[0]
        assert_true(test.has_custom_metadata)
        metadata = dict(test.custom_metadata)
        assert_equal(metadata, {"Owner": "Alice", "Priority": "High"})
        assert_false("Component" in metadata)
        assert_false("NotAllowed" in metadata)
        
        # Test with empty list (no metadata included)
        suite = self._build_from_string(data, custom_metadata=[])
        test = suite.tests[0]
        assert_false(test.has_custom_metadata)
        assert_equal(dict(test.custom_metadata), {})

    def test_custom_metadata_in_keywords_and_mixed_settings(self):
        """Test custom metadata in keywords and mixed with regular settings."""
        data = dedent("""\
            *** Keywords ***
            My Keyword With Metadata
                [Owner]           Bob
                [Complexity]      Low
                [API]             /api/users
                Log               Keyword body
                
            *** Test Cases ***
            Mixed Settings Test
                [Documentation]   Test documentation
                [Owner]           Charlie
                [Tags]            regression  critical
                [Priority]        Medium
                [Setup]           Log  Setup
                [Component]       Core
                [Teardown]        Log  Teardown
                My Keyword With Metadata
                Log               Test body
        """)
        
        suite = self._build_from_string(data, custom_metadata=["Owner", "Priority", "API"])
        
        # Check keyword metadata
        keyword = suite.resource.keywords[0]
        assert_true(hasattr(keyword, 'custom_metadata'))
        assert_true(keyword.has_custom_metadata)
        kw_metadata = dict(keyword.custom_metadata)
        assert_equal(kw_metadata["Owner"], "Bob")
        assert_equal(kw_metadata["API"], "/api/users")
        assert_false("Complexity" in kw_metadata)  # Filtered out
        
        # Check test metadata and regular settings
        test = suite.tests[0]
        assert_equal(test.doc, "Test documentation")
        assert_equal(list(test.tags), ["critical", "regression"])  # Tags are sorted
        assert_equal(test.setup.name, "Log")
        assert_equal(test.teardown.name, "Log")
        
        # Check filtered custom metadata
        test_metadata = dict(test.custom_metadata)
        assert_equal(test_metadata, {"Owner": "Charlie", "Priority": "Medium"})
        assert_false("Component" in test_metadata)  # Filtered out

    def test_custom_metadata_special_values_and_continuation(self):
        """Test custom metadata with special values, continuation, and edge cases."""
        data = dedent("""\
            *** Test Cases ***
            Special Values Test
                [Description]     This is a very long description
                ...               that continues on the next line
                [Owner]           
                [Priority]        High
                [Component]       
                [Bug-ID]          BUG-1234
                [Test_Level]      Component
                [Version 2.0]     Compatible
                [Owner/Reviewer]  Alice/Bob
                Log               Test
        """)
        
        suite = self._build_from_string(data)
        test = suite.tests[0]
        assert_true(test.has_custom_metadata)
        metadata = dict(test.custom_metadata)
        
        # Test line continuation
        expected_desc = "This is a very long description that continues on the next line"
        assert_equal(metadata["Description"], expected_desc)
        
        # Test empty values
        assert_equal(metadata["Owner"], "")
        assert_equal(metadata["Priority"], "High")
        assert_equal(metadata["Component"], "")
        
        # Test special characters
        assert_equal(metadata["Bug-ID"], "BUG-1234")
        assert_equal(metadata["Test_Level"], "Component")
        assert_equal(metadata["Version 2.0"], "Compatible")
        assert_equal(metadata["Owner/Reviewer"], "Alice/Bob")

    def test_custom_metadata_case_sensitivity_and_multiple_tests(self):
        """Test case sensitivity in filtering and multiple test scenarios."""
        data = dedent("""\
            *** Test Cases ***
            Case Sensitive Test
                [Owner]           Alice
                [owner]           Bob
                [OWNER]           Charlie
                Log               Hello
                
            First Test
                [Owner]           TestOwner1
                [Priority]        High
                Log               First test
                
            Second Test
                [Owner]           TestOwner2
                [Component]       Backend
                Log               Second test
                
            Third Test
                Log               No metadata
        """)
        
        # Test case sensitivity in filtering
        suite = self._build_from_string(data, custom_metadata=["Owner"])
        test1 = suite.tests[0]
        assert_true(test1.has_custom_metadata)
        metadata = dict(test1.custom_metadata)
        # Due to normalization, only one should exist
        assert_equal(len(metadata), 1)
        assert_true("Owner" in metadata or "owner" in metadata or "OWNER" in metadata)
        
        # Test multiple tests with different metadata
        test2 = suite.tests[1]
        assert_true(test2.has_custom_metadata)
        assert_equal(test2.custom_metadata["Owner"], "TestOwner1")
        assert_false("Priority" in dict(test2.custom_metadata))  # Filtered out
        
        test3 = suite.tests[2] 
        assert_true(test3.has_custom_metadata)
        assert_equal(test3.custom_metadata["Owner"], "TestOwner2")
        assert_false("Component" in dict(test3.custom_metadata))  # Filtered out
        
        test4 = suite.tests[3]
        assert_false(test4.has_custom_metadata)

    def test_file_settings_and_integration_scenarios(self):
        """Test FileSettings configuration and integration scenarios."""
        from robot.conf import Languages
        from robot.parsing.lexer.settings import SuiteFileSettings
        
        # Test FileSettings with different configurations
        settings_none = SuiteFileSettings(Languages())
        assert_equal(settings_none.allowed_custom_metadata, None)
        assert_true(settings_none.is_custom_metadata_allowed("Owner"))
        
        # Test with specific allowed metadata
        allowed = ["Owner", "Priority", "Component"]
        settings_allowed = SuiteFileSettings(Languages(), allowed_custom_metadata=allowed)
        assert_equal(settings_allowed.allowed_custom_metadata, allowed)
        assert_true(settings_allowed.is_custom_metadata_allowed("Owner"))
        assert_false(settings_allowed.is_custom_metadata_allowed("NotAllowed"))
        
        # Test with empty allowed list
        settings_empty = SuiteFileSettings(Languages(), allowed_custom_metadata=[])
        assert_equal(settings_empty.allowed_custom_metadata, [])
        assert_false(settings_empty.is_custom_metadata_allowed("Owner"))
        
        # Test case sensitivity in FileSettings
        settings_case = SuiteFileSettings(Languages(), allowed_custom_metadata=["Owner", "priority"])
        assert_true(settings_case.is_custom_metadata_allowed("Owner"))
        assert_true(settings_case.is_custom_metadata_allowed("priority"))
        assert_false(settings_case.is_custom_metadata_allowed("owner"))  # Different case
        assert_false(settings_case.is_custom_metadata_allowed("Priority"))  # Different case


if __name__ == "__main__":
    unittest.main()
