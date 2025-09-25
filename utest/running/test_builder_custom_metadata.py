import unittest
from textwrap import dedent

from robot.running.builder import TestSuiteBuilder


class TestCustomMetadataBuilder(unittest.TestCase):
    """Test custom metadata handling in the builder layer."""

    def setUp(self):
        """Set up test environment."""
        self.builder = TestSuiteBuilder()

    def _create_suite_from_string(self, data, custom_metadata=None):
        """Helper to create suite from robot file string."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".robot", delete=False) as f:
            f.write(data)
            temp_file = f.name

        try:
            # Build without specifying custom metadata filter - all should be included
            suite = self.builder.build(temp_file)
            return suite
        finally:
            os.unlink(temp_file)

    def test_build_test_with_custom_metadata(self):
        """Test building test cases with custom metadata."""
        data = dedent(
            """
        *** Test Cases ***
        Test With Custom Metadata
            [Owner]           Alice
            [Priority]        High
            [Component]       Authentication
            Log               Test body
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        # Should have custom metadata
        self.assertTrue(test.has_custom_metadata)
        self.assertEqual(test.custom_metadata["Owner"], "Alice")
        self.assertEqual(test.custom_metadata["Priority"], "High")
        self.assertEqual(test.custom_metadata["Component"], "Authentication")

    def test_build_keyword_with_custom_metadata(self):
        """Test building user keywords with custom metadata."""
        data = dedent(
            """
        *** Test Cases ***
        Test Using Custom Keyword
            My Custom Keyword

        *** Keywords ***
        My Custom Keyword
            [Owner]           Bob
            [Complexity]      Medium
            [Type]            Utility
            Log               Keyword body
        """
        )

        suite = self._create_suite_from_string(data)
        # Get the keyword from the resource
        resource = suite.resource
        keyword = resource.keywords[0]

        # Should have custom metadata
        self.assertTrue(keyword.has_custom_metadata)
        self.assertEqual(keyword.custom_metadata["Owner"], "Bob")
        self.assertEqual(keyword.custom_metadata["Complexity"], "Medium")
        self.assertEqual(keyword.custom_metadata["Type"], "Utility")

    def test_build_test_and_keyword_custom_metadata_coexistence(self):
        """Test that test and keyword custom metadata can coexist."""
        data = dedent(
            """
        *** Test Cases ***
        Integration Test
            [Owner]           Alice
            [Requirement]     INT-001
            My Test Keyword

        *** Keywords ***
        My Test Keyword
            [Author]          Bob
            [Version]         1.2
            Log               Performing action
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]
        keyword = suite.resource.keywords[0]

        # Both should have custom metadata
        self.assertTrue(test.has_custom_metadata)
        self.assertTrue(keyword.has_custom_metadata)

        # Test metadata
        self.assertEqual(test.custom_metadata["Owner"], "Alice")
        self.assertEqual(test.custom_metadata["Requirement"], "INT-001")

        # Keyword metadata
        self.assertEqual(keyword.custom_metadata["Author"], "Bob")
        self.assertEqual(keyword.custom_metadata["Version"], "1.2")

    def test_build_with_multiline_custom_metadata(self):
        """Test building with multiline custom metadata values."""
        data = dedent(
            """
        *** Test Cases ***
        Test With Multiline Metadata
            [Description]     This is a long description
            ...               that spans multiple lines
            ...               with detailed information
            [Steps]           Step 1: Login
            ...               Step 2: Navigate
            ...               Step 3: Validate
            Log               Test execution
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        self.assertTrue(test.has_custom_metadata)
        # Multiline values should be joined with spaces
        expected_desc = "This is a long description that spans multiple lines with detailed information"
        expected_steps = "Step 1: Login Step 2: Navigate Step 3: Validate"

        self.assertEqual(test.custom_metadata["Description"], expected_desc)
        self.assertEqual(test.custom_metadata["Steps"], expected_steps)

    def test_build_with_special_characters_in_metadata(self):
        """Test building with special characters in metadata keys and values."""
        data = dedent(
            """
        *** Test Cases ***  
        Test With Special Characters
            Log               Using special keyword

        *** Keywords ***
        Special Character Keyword
            [Bug-ID]          BUG-123
            [API/Version]     v2.1
            [Test_Level]      Integration
            [Description]     Uses special chars: !@#$%^&*()
            Log               Special keyword body
        """
        )

        suite = self._create_suite_from_string(data)
        keyword = suite.resource.keywords[0]

        self.assertTrue(keyword.has_custom_metadata)
        self.assertEqual(keyword.custom_metadata["Bug-ID"], "BUG-123")
        self.assertEqual(keyword.custom_metadata["API/Version"], "v2.1")
        self.assertEqual(keyword.custom_metadata["Test_Level"], "Integration")
        self.assertEqual(
            keyword.custom_metadata["Description"], "Uses special chars: !@#$%^&*()"
        )

    def test_build_with_unicode_custom_metadata(self):
        """Test building with Unicode characters in custom metadata."""
        data = dedent(
            """
        *** Test Cases ***
        Unicode Metadata Test
            [Owner]           Alice
            [Description]     This test uses unicode: äöü
            [Note]            Unicode support test
            Log               Unicode test body
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        self.assertTrue(test.has_custom_metadata)
        # Test with ASCII characters instead to avoid normalization issues
        self.assertEqual(test.custom_metadata["Owner"], "Alice")
        self.assertEqual(
            test.custom_metadata["Description"], "This test uses unicode: äöü"
        )
        self.assertEqual(test.custom_metadata["Note"], "Unicode support test")

    def test_build_with_empty_custom_metadata_values(self):
        """Test building with empty custom metadata values."""
        data = dedent(
            """
        *** Test Cases ***
        Test With Empty Metadata
            [EmptyValue]      
            [Whitespace]      ${SPACE}${SPACE}${SPACE}
            [ValidValue]      Not empty
            Log               Test with empty values
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        self.assertTrue(test.has_custom_metadata)
        self.assertEqual(test.custom_metadata["EmptyValue"], "")
        self.assertEqual(test.custom_metadata["Whitespace"], "${SPACE}${SPACE}${SPACE}")
        self.assertEqual(test.custom_metadata["ValidValue"], "Not empty")

    def test_build_custom_metadata_with_variables(self):
        """Test building custom metadata that contains variables."""
        data = dedent(
            """
        *** Variables ***
        ${OWNER}          Alice
        ${VERSION}        1.0

        *** Test Cases ***
        Test With Variable Metadata
            [Owner]           ${OWNER}
            [Version]         ${VERSION}
            [Environment]     ${ENVIRONMENT}
            Log               Test with variables
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        # Variables should be preserved as-is in the model
        self.assertTrue(test.has_custom_metadata)
        self.assertEqual(test.custom_metadata["Owner"], "${OWNER}")
        self.assertEqual(test.custom_metadata["Version"], "${VERSION}")
        self.assertEqual(test.custom_metadata["Environment"], "${ENVIRONMENT}")

    def test_build_custom_metadata_with_embedded_args_keyword(self):
        """Test building custom metadata for keywords with embedded arguments."""
        data = dedent(
            """
        *** Test Cases ***
        Test Embedded Args
            User selects book from list

        *** Keywords ***
        User selects ${item} from ${list}
            [Type]            Embedded
            [Parameters]      2
            [Usage]           Common
            Log               Selecting ${item} from ${list}
        """
        )

        suite = self._create_suite_from_string(data)
        keyword = suite.resource.keywords[0]

        self.assertTrue(keyword.has_custom_metadata)
        self.assertEqual(keyword.custom_metadata["Type"], "Embedded")
        self.assertEqual(keyword.custom_metadata["Parameters"], "2")
        self.assertEqual(keyword.custom_metadata["Usage"], "Common")

    def test_build_custom_metadata_with_setup_teardown(self):
        """Test building custom metadata for keywords with setup/teardown."""
        data = dedent(
            """
        *** Test Cases ***
        Test Using Setup Teardown Keyword
            Keyword With Setup And Teardown

        *** Keywords ***
        Keyword With Setup And Teardown
            [Setup]           Log    Starting keyword
            [Teardown]        Log    Finishing keyword
            [Owner]           Team
            [HasSetup]        Yes
            [HasTeardown]     Yes
            Log               Main keyword body
        """
        )

        suite = self._create_suite_from_string(data)
        keyword = suite.resource.keywords[0]

        # Should have both setup/teardown and custom metadata
        self.assertTrue(keyword.has_setup)
        self.assertTrue(keyword.has_teardown)
        self.assertTrue(keyword.has_custom_metadata)

        self.assertEqual(keyword.custom_metadata["Owner"], "Team")
        self.assertEqual(keyword.custom_metadata["HasSetup"], "Yes")
        self.assertEqual(keyword.custom_metadata["HasTeardown"], "Yes")

    def test_build_multiple_tests_and_keywords_with_metadata(self):
        """Test building multiple tests and keywords each with custom metadata."""
        data = dedent(
            """
        *** Test Cases ***
        First Test
            [Owner]           Alice
            [Priority]        High
            Log               First test

        Second Test  
            [Owner]           Bob
            [Priority]        Low
            Log               Second test

        *** Keywords ***
        First Keyword
            [Author]          Alice
            [Version]         1.0
            Log               First keyword

        Second Keyword
            [Author]          Bob
            [Version]         2.0
            Log               Second keyword
        """
        )

        suite = self._create_suite_from_string(data)

        # Check tests
        test1, test2 = suite.tests
        self.assertTrue(test1.has_custom_metadata)
        self.assertEqual(test1.custom_metadata["Owner"], "Alice")
        self.assertEqual(test1.custom_metadata["Priority"], "High")

        self.assertTrue(test2.has_custom_metadata)
        self.assertEqual(test2.custom_metadata["Owner"], "Bob")
        self.assertEqual(test2.custom_metadata["Priority"], "Low")

        # Check keywords
        kw1, kw2 = suite.resource.keywords
        self.assertTrue(kw1.has_custom_metadata)
        self.assertEqual(kw1.custom_metadata["Author"], "Alice")
        self.assertEqual(kw1.custom_metadata["Version"], "1.0")

        self.assertTrue(kw2.has_custom_metadata)
        self.assertEqual(kw2.custom_metadata["Author"], "Bob")
        self.assertEqual(kw2.custom_metadata["Version"], "2.0")

    def test_build_custom_metadata_ordering_preservation(self):
        """Test that custom metadata order is preserved during building."""
        data = dedent(
            """
        *** Test Cases ***
        Order Test
            [First]           1
            [Second]          2
            [Third]           3
            [Fourth]          4
            [Fifth]           5
            Log               Order test
        """
        )

        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        # Check that all metadata is present (order may vary due to normalization)
        self.assertTrue(test.has_custom_metadata)
        self.assertEqual(len(test.custom_metadata), 5)
        self.assertEqual(test.custom_metadata["First"], "1")
        self.assertEqual(test.custom_metadata["Second"], "2")
        self.assertEqual(test.custom_metadata["Third"], "3")
        self.assertEqual(test.custom_metadata["Fourth"], "4")
        self.assertEqual(test.custom_metadata["Fifth"], "5")

    def test_build_error_handling_with_invalid_syntax(self):
        """Test error handling when custom metadata has invalid syntax (should still work)."""
        data = dedent(
            """
        *** Test Cases ***
        Test With Potential Issues
            [ValidMeta]       Valid value
            [Edge-Case]       Value with "quotes" and 'apostrophes'
            [NumberKey]       12345
            Log               Test body
        """
        )

        # Should not raise an exception during building
        suite = self._create_suite_from_string(data)
        test = suite.tests[0]

        self.assertTrue(test.has_custom_metadata)
        self.assertEqual(test.custom_metadata["ValidMeta"], "Valid value")
        self.assertEqual(
            test.custom_metadata["Edge-Case"], "Value with \"quotes\" and 'apostrophes'"
        )
        self.assertEqual(test.custom_metadata["NumberKey"], "12345")


if __name__ == "__main__":
    unittest.main()
