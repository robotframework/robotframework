import unittest

from robot.parsing import get_tokens, Token
from robot.utils.asserts import assert_equal

T = Token


def assert_tokens(source, expected, get_tokens=get_tokens, **config):
    tokens = list(get_tokens(source, **config))
    assert_equal(
        len(tokens),
        len(expected),
        f"Expected {len(expected)} tokens:\n{format_tokens(expected)}\n\n"
        f"Got {len(tokens)} tokens:\n{format_tokens(tokens)}",
        values=False,
    )
    for act, exp in zip(tokens, expected):
        assert_equal(act, Token(*exp), formatter=repr)


def format_tokens(tokens):
    return "\n".join(repr(t) for t in tokens)


class TestCustomMetadataLexer(unittest.TestCase):
    """Test custom metadata parsing in lexer layer."""

    def test_custom_metadata_basic_parsing(self):
        """Test basic custom metadata parsing with and without filtering."""
        # Test without filtering
        data = """\
*** Test Cases ***
Test With Custom Metadata
    [Owner]           Alice
    [Priority]        High
    [Component]       UI
    Log               Hello

*** Keywords ***
My Keyword
    [Owner]           Bob
    [Complexity]      Low
    Log               Keyword body
"""
        expected_no_filter = [
            (T.TESTCASE_HEADER, "*** Test Cases ***", 1, 0),
            (T.EOS, "", 1, 18),
            (T.TESTCASE_NAME, "Test With Custom Metadata", 2, 0),
            (T.EOS, "", 2, 25),
            (T.CUSTOM_METADATA, "[Owner]", 3, 4),
            (T.ARGUMENT, "Alice", 3, 22),
            (T.EOS, "", 3, 27),
            (T.CUSTOM_METADATA, "[Priority]", 4, 4),
            (T.ARGUMENT, "High", 4, 22),
            (T.EOS, "", 4, 26),
            (T.CUSTOM_METADATA, "[Component]", 5, 4),
            (T.ARGUMENT, "UI", 5, 22),
            (T.EOS, "", 5, 24),
            (T.KEYWORD, "Log", 6, 4),
            (T.ARGUMENT, "Hello", 6, 22),
            (T.EOS, "", 6, 27),
            (T.KEYWORD_HEADER, "*** Keywords ***", 8, 0),
            (T.EOS, "", 8, 16),
            (T.KEYWORD_NAME, "My Keyword", 9, 0),
            (T.EOS, "", 9, 10),
            (T.CUSTOM_METADATA, "[Owner]", 10, 4),
            (T.ARGUMENT, "Bob", 10, 22),
            (T.EOS, "", 10, 25),
            (T.CUSTOM_METADATA, "[Complexity]", 11, 4),
            (T.ARGUMENT, "Low", 11, 22),
            (T.EOS, "", 11, 25),
            (T.KEYWORD, "Log", 12, 4),
            (T.ARGUMENT, "Keyword body", 12, 22),
            (T.EOS, "", 12, 34),
        ]
        assert_tokens(data, expected_no_filter, data_only=True)

        # Test with filtering - only Owner allowed
        expected_filtered = [
            (T.TESTCASE_HEADER, "*** Test Cases ***", 1, 0),
            (T.EOS, "", 1, 18),
            (T.TESTCASE_NAME, "Test With Custom Metadata", 2, 0),
            (T.EOS, "", 2, 25),
            (T.CUSTOM_METADATA, "[Owner]", 3, 4),
            (T.ARGUMENT, "Alice", 3, 22),
            (T.EOS, "", 3, 27),
            (T.CUSTOM_METADATA, "[Priority]", 4, 4),
            (T.ARGUMENT, "High", 4, 22),
            (T.EOS, "", 4, 26),
            (T.CUSTOM_METADATA, "[Component]", 5, 4),
            (T.ARGUMENT, "UI", 5, 22),
            (T.EOS, "", 5, 24),
            (T.KEYWORD, "Log", 6, 4),
            (T.ARGUMENT, "Hello", 6, 22),
            (T.EOS, "", 6, 27),
            (T.KEYWORD_HEADER, "*** Keywords ***", 8, 0),
            (T.EOS, "", 8, 16),
            (T.KEYWORD_NAME, "My Keyword", 9, 0),
            (T.EOS, "", 9, 10),
            (T.CUSTOM_METADATA, "[Owner]", 10, 4),
            (T.ARGUMENT, "Bob", 10, 22),
            (T.EOS, "", 10, 25),
            (T.CUSTOM_METADATA, "[Complexity]", 11, 4),
            (T.ARGUMENT, "Low", 11, 22),
            (T.EOS, "", 11, 25),
            (T.KEYWORD, "Log", 12, 4),
            (T.ARGUMENT, "Keyword body", 12, 22),
            (T.EOS, "", 12, 34),
        ]
        assert_tokens(
            data, expected_filtered, data_only=True, allowed_custom_metadata=["Owner"]
        )

    def test_custom_metadata_mixed_with_regular_settings(self):
        """Test custom metadata mixed with regular settings and multiple values."""
        data = """\
*** Test Cases ***
Mixed Settings Test
    [Documentation]   Test documentation
    [Owner]           Charlie
    [Tags]            regression  critical
    [Reviewers]       Alice    Bob    Charlie
    [Priority]        Medium
    [Setup]           Log  Setup
    [Component]       Core
    Log               Test body
"""
        expected = [
            (T.TESTCASE_HEADER, "*** Test Cases ***", 1, 0),
            (T.EOS, "", 1, 18),
            (T.TESTCASE_NAME, "Mixed Settings Test", 2, 0),
            (T.EOS, "", 2, 19),
            (T.DOCUMENTATION, "[Documentation]", 3, 4),
            (T.ARGUMENT, "Test documentation", 3, 22),
            (T.EOS, "", 3, 40),
            (T.CUSTOM_METADATA, "[Owner]", 4, 4),
            (T.ARGUMENT, "Charlie", 4, 22),
            (T.EOS, "", 4, 29),
            (T.TAGS, "[Tags]", 5, 4),
            (T.ARGUMENT, "regression", 5, 22),
            (T.ARGUMENT, "critical", 5, 34),
            (T.EOS, "", 5, 42),
            (T.CUSTOM_METADATA, "[Reviewers]", 6, 4),
            (T.ARGUMENT, "Alice", 6, 22),
            (T.ARGUMENT, "Bob", 6, 31),
            (T.ARGUMENT, "Charlie", 6, 38),
            (T.EOS, "", 6, 45),
            (T.CUSTOM_METADATA, "[Priority]", 7, 4),
            (T.ARGUMENT, "Medium", 7, 22),
            (T.EOS, "", 7, 28),
            (T.SETUP, "[Setup]", 8, 4),
            (T.NAME, "Log", 8, 22),
            (T.ARGUMENT, "Setup", 8, 27),
            (T.EOS, "", 8, 32),
            (T.CUSTOM_METADATA, "[Component]", 9, 4),
            (T.ARGUMENT, "Core", 9, 22),
            (T.EOS, "", 9, 26),
            (T.KEYWORD, "Log", 10, 4),
            (T.ARGUMENT, "Test body", 10, 22),
            (T.EOS, "", 10, 31),
        ]
        assert_tokens(data, expected, data_only=True)

    def test_custom_metadata_special_cases_and_validation(self):
        """Test special characters, edge cases, and validation."""
        data = """\
*** Test Cases ***
Special Cases Test
    [Bug-ID]          BUG-1234
    [Test_Level]      Component
    [Version 2.0]     Compatible
    [Owner]
    []                Empty brackets
    [123]             Number only
    [@invalid]        Special char start
    Log               Test

*** Settings ***
[Owner]           Alice
Documentation     Suite doc
"""
        expected = [
            (T.TESTCASE_HEADER, "*** Test Cases ***", 1, 0),
            (T.EOS, "", 1, 18),
            (T.TESTCASE_NAME, "Special Cases Test", 2, 0),
            (T.EOS, "", 2, 18),
            (T.CUSTOM_METADATA, "[Bug-ID]", 3, 4),
            (T.ARGUMENT, "BUG-1234", 3, 22),
            (T.EOS, "", 3, 30),
            (T.CUSTOM_METADATA, "[Test_Level]", 4, 4),
            (T.ARGUMENT, "Component", 4, 22),
            (T.EOS, "", 4, 31),
            (T.CUSTOM_METADATA, "[Version 2.0]", 5, 4),
            (T.ARGUMENT, "Compatible", 5, 22),
            (T.EOS, "", 5, 32),
            (T.CUSTOM_METADATA, "[Owner]", 6, 4),
            (T.EOS, "", 6, 11),
            (T.ERROR, "[]", 7, 4, "Non-existing setting ''."),
            (T.EOS, "", 7, 6),
            (T.CUSTOM_METADATA, "[123]", 8, 4),
            (T.ARGUMENT, "Number only", 8, 22),
            (T.EOS, "", 8, 33),
            (T.ERROR, "[@invalid]", 9, 4, "Non-existing setting '@invalid'."),
            (T.EOS, "", 9, 14),
            (T.KEYWORD, "Log", 10, 4),
            (T.ARGUMENT, "Test", 10, 22),
            (T.EOS, "", 10, 26),
            (T.SETTING_HEADER, "*** Settings ***", 12, 0),
            (T.EOS, "", 12, 16),
            (
                T.ERROR,
                "[Owner]",
                13,
                0,
                "Custom metadata is not allowed in this context.",
            ),
            (T.EOS, "", 13, 7),
            (T.DOCUMENTATION, "Documentation", 14, 0),
            (T.ARGUMENT, "Suite doc", 14, 18),
            (T.EOS, "", 14, 27),
        ]
        assert_tokens(data, expected, data_only=True)

    def test_custom_metadata_edge_cases_and_continuation(self):
        """Test edge cases including continuation, case sensitivity, and long values."""
        # Test continuation and case sensitivity
        data = """\
*** Test Cases ***
Edge Cases Test
    [Owner]           Alice
    [owner]           Bob
    [PRIORITY]        High
    [Description]     This is a very long description
    ...               that continues on the next line
    Log               Test
"""
        expected = [
            (T.TESTCASE_HEADER, "*** Test Cases ***", 1, 0),
            (T.EOS, "", 1, 18),
            (T.TESTCASE_NAME, "Edge Cases Test", 2, 0),
            (T.EOS, "", 2, 15),
            (T.CUSTOM_METADATA, "[Owner]", 3, 4),
            (T.ARGUMENT, "Alice", 3, 22),
            (T.EOS, "", 3, 27),
            (T.CUSTOM_METADATA, "[owner]", 4, 4),
            (T.ARGUMENT, "Bob", 4, 22),
            (T.EOS, "", 4, 25),
            (T.CUSTOM_METADATA, "[PRIORITY]", 5, 4),
            (T.ARGUMENT, "High", 5, 22),
            (T.EOS, "", 5, 26),
            (T.CUSTOM_METADATA, "[Description]", 6, 4),
            (T.ARGUMENT, "This is a very long description", 6, 22),
            (T.ARGUMENT, "that continues on the next line", 7, 22),
            (T.EOS, "", 7, 53),
            (T.KEYWORD, "Log", 8, 4),
            (T.ARGUMENT, "Test", 8, 22),
            (T.EOS, "", 8, 26),
        ]
        assert_tokens(data, expected, data_only=True, allowed_custom_metadata=["Owner"])

        # Test with long values
        long_value = "A" * 100
        long_data = f"*** Test Cases ***\nLong Value Test\n    [Owner]           {long_value}\n    Log               Test\n"
        long_expected = [
            (T.TESTCASE_HEADER, "*** Test Cases ***", 1, 0),
            (T.EOS, "", 1, 18),
            (T.TESTCASE_NAME, "Long Value Test", 2, 0),
            (T.EOS, "", 2, 15),
            (T.CUSTOM_METADATA, "[Owner]", 3, 4),
            (T.ARGUMENT, long_value, 3, 22),
            (T.EOS, "", 3, 122),
            (T.KEYWORD, "Log", 4, 4),
            (T.ARGUMENT, "Test", 4, 22),
            (T.EOS, "", 4, 26),
        ]
        assert_tokens(long_data, long_expected, data_only=True)


if __name__ == "__main__":
    unittest.main()
