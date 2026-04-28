import unittest


class TestCustomMetadataCommandLineIntegration(unittest.TestCase):
    """Test command line option parsing for --custommetadata."""

    def test_custom_metadata_option_exists(self):
        """Test that --custommetadata option is properly defined in CLI help."""
        from robot.run import USAGE

        # Check that the --custommetadata option is documented in help
        self.assertIn("--custommetadata", USAGE)
        self.assertIn("custom metadata", USAGE.lower())

    def test_file_settings_custom_metadata_propagation(self):
        """Test that custom metadata settings propagate through FileSettings."""
        from robot.running.builder.settings import FileSettings

        # Test default (None) - all metadata allowed
        settings = FileSettings(custom_metadata=None)
        self.assertTrue(settings.should_include_custom_metadata("Owner"))
        self.assertTrue(settings.should_include_custom_metadata("Priority"))
        self.assertTrue(settings.should_include_custom_metadata("AnyName"))

        # Test empty list - no metadata allowed
        settings = FileSettings(custom_metadata=[])
        self.assertFalse(settings.should_include_custom_metadata("Owner"))
        self.assertFalse(settings.should_include_custom_metadata("Priority"))
        self.assertFalse(settings.should_include_custom_metadata("AnyName"))

        # Test specific list - only specified metadata allowed
        settings = FileSettings(custom_metadata=["Owner", "Priority"])
        self.assertTrue(settings.should_include_custom_metadata("Owner"))
        self.assertTrue(settings.should_include_custom_metadata("Priority"))
        self.assertFalse(settings.should_include_custom_metadata("Component"))
        self.assertFalse(settings.should_include_custom_metadata("AnyName"))

    def test_custom_metadata_node_parsing(self):
        """Test that CustomMetadata nodes are properly parsed."""
        from robot.parsing import Token
        from robot.parsing.model.statements import CustomMetadata

        # Create a mock custom metadata node
        node = CustomMetadata(
            [
                Token(Token.SEPARATOR, "    "),
                Token(Token.CUSTOM_METADATA, "[Owner]"),
                Token(Token.SEPARATOR, "    "),
                Token(Token.ARGUMENT, "John Doe"),
            ]
        )

        # The node should provide the key and value correctly
        self.assertEqual(node.key, "Owner")
        self.assertEqual(node.value, "John Doe")

        # Test with multiline value
        multiline_node = CustomMetadata(
            [
                Token(Token.SEPARATOR, "    "),
                Token(Token.CUSTOM_METADATA, "[Description]"),
                Token(Token.SEPARATOR, "    "),
                Token(Token.ARGUMENT, "First line"),
                Token(Token.EOL, "\n"),
                Token(Token.CONTINUATION, "..."),
                Token(Token.SEPARATOR, "    "),
                Token(Token.ARGUMENT, "Second line"),
            ]
        )

        self.assertEqual(multiline_node.key, "Description")
        # The value should include the multiline content
        self.assertIn("First line", multiline_node.value)

    def test_case_sensitivity_filtering(self):
        """Test case sensitivity of metadata filtering."""
        from robot.running.builder.settings import FileSettings

        # Test case sensitivity - metadata names are case sensitive in filtering
        settings = FileSettings(
            custom_metadata=["Owner", "priority"]
        )  # lowercase priority

        self.assertTrue(settings.should_include_custom_metadata("Owner"))
        self.assertTrue(
            settings.should_include_custom_metadata("priority")
        )  # exact match
        self.assertFalse(
            settings.should_include_custom_metadata("Priority")
        )  # different case
        self.assertFalse(
            settings.should_include_custom_metadata("OWNER")
        )  # different case

    def test_empty_and_none_filtering(self):
        """Test edge cases with None and empty list filtering."""
        from robot.running.builder.settings import FileSettings

        # Test None allows everything
        settings_none = FileSettings(custom_metadata=None)
        self.assertTrue(
            settings_none.should_include_custom_metadata("")
        )  # even empty string
        self.assertTrue(settings_none.should_include_custom_metadata("AnyName"))

        # Test empty list blocks everything
        settings_empty = FileSettings(custom_metadata=[])
        self.assertFalse(settings_empty.should_include_custom_metadata("Owner"))
        self.assertFalse(settings_empty.should_include_custom_metadata(""))

        # Test list with empty string
        settings_with_empty = FileSettings(custom_metadata=[""])
        self.assertTrue(settings_with_empty.should_include_custom_metadata(""))
        self.assertFalse(settings_with_empty.should_include_custom_metadata("Owner"))

    def test_whitespace_handling_in_names(self):
        """Test that whitespace in metadata names is handled correctly."""
        from robot.running.builder.settings import FileSettings

        settings = FileSettings(custom_metadata=["My Name", "Owner"])

        self.assertTrue(settings.should_include_custom_metadata("My Name"))
        self.assertTrue(settings.should_include_custom_metadata("Owner"))
        self.assertFalse(settings.should_include_custom_metadata("MyName"))  # no space
        self.assertFalse(
            settings.should_include_custom_metadata("My  Name")
        )  # double space


if __name__ == "__main__":
    unittest.main()
