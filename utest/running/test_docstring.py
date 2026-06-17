import unittest

from robot.running.docstring import parse_docstring, ParsedDocString
from robot.utils.asserts import assert_equal


class TestPlainDocstring(unittest.TestCase):

    def test_no_sections_returns_doc_unchanged(self):
        doc = "Does something useful."
        result = parse_docstring(doc)
        assert_equal(
            result, ParsedDocString(doc="Does something useful.", args={}, returns="")
        )

    def test_empty_string(self):
        result = parse_docstring("")
        assert_equal(result, ParsedDocString(doc="", args={}, returns=""))

    def test_multiline_plain_docstring(self):
        doc = """\
First line.

More detail here."""
        result = parse_docstring(doc)
        assert_equal(
            result,
            ParsedDocString(
                doc=doc,
                args={},
                returns="",
            ),
        )

    def test_leading_blank_line_stripped(self):
        doc = """\

Summary."""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")


class TestArgsSection(unittest.TestCase):

    def test_single_inline_arg(self):
        doc = """\
Summary line.

Args:
    name: The name to use.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary line.")
        assert_equal(result.args, {"name": "The name to use."})
        assert_equal(result.returns, "")

    def test_multiple_inline_args(self):
        doc = """\
Summary.

Args:
    first: First argument.
    second: Second argument.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"first": "First argument.", "second": "Second argument."},
        )

    def test_duplicate_arg_name_last_wins(self):
        doc = """\
Summary.

Args:
    name: First occurrence.
    name: Second occurrence.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"name": "Second occurrence."})

    def test_block_format_arg(self):
        doc = """\
Summary.

Args:
    name:
        Description on next line.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "Description on next line."},
        )

    def test_multiline_arg_description(self):
        doc = """\
Summary.

Args:
    name: First line of description
        that continues here.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "First line of description that continues here."},
        )

    def test_inline_arg_with_blank_line_preserves_paragraph_break(self):
        doc = """\
Summary.

Args:
    name: First paragraph.

        Second paragraph.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "First paragraph.\n\nSecond paragraph."},
        )

    def test_deep_indented_code_block_in_arg_description(self):
        doc = """\
Summary.

Args:
    name:
        Some doc here. With example:

               def example():
                   pass

        And more doc here.

    name2: Some other doc.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {
                "name": """\
Some doc here. With example:

       def example():
           pass

And more doc here.""",
                "name2": "Some other doc.",
            },
        )
        assert_equal(result.returns, "")
        assert_equal(result.doc, "Summary.")

    def test_second_arg_with_smaller_indent_than_first_is_still_detected(self):
        doc = """\
Summary.

Args:
    name:
        Some doc here.

   name2: Some other doc.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "Some doc here.", "name2": "Some other doc."},
        )

    def test_deeply_indented_name_colon_is_not_a_new_arg(self):
        doc = """\
Summary.

Args:
    name:
        Some doc here.

        name2: still doc of "name" arg, not new arg.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {
                "name": """Some doc here.

name2: still doc of "name" arg, not new arg."""
            },
        )

    def test_block_arg_body_with_inconsistent_indentation(self):
        doc = """\
Summary.

Args:
    name:
        Some doc here.

      And more doc here.

    name2: Some other doc.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {
                "name": """Some doc here.

And more doc here.""",
                "name2": "Some other doc.",
            },
        )

    def test_arguments_header_accepted(self):
        doc = """\
Summary.

Arguments:
    name: The name.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"name": "The name."})

    def test_parameters_header_accepted(self):
        doc = """\
Summary.

Parameters:
    name: The name.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"name": "The name."})

    def test_lowercase_args_recognised(self):
        doc = """\
Summary.

args:
    name: value.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(result.args, {"name": "value."})
        assert_equal(result.returns, "")

    def test_args_with_colon_in_description(self):
        doc = """\
Summary.

Args:
    url: https://example.com is the target.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"url": "https://example.com is the target."},
        )


class TestReturnsSection(unittest.TestCase):

    def test_returns_section(self):
        doc = """\
Summary.

Returns:
    The result value.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(result.args, {})
        assert_equal(result.returns, "The result value.")

    def test_yields_header_goes_into_returns(self):
        doc = """\
Summary.

Yields:
    One item at a time.
"""
        result = parse_docstring(doc)
        assert_equal(result.returns, "One item at a time.")

    def test_multiline_returns(self):
        doc = """\
Summary.

Returns:
    First line of return description
    that continues here.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.returns,
            """\
First line of return description
that continues here.""",
        )

    def test_multiple_returns_sections_last_wins(self):
        doc = """\
Summary.

Returns:
    First return.

Returns:
    Second return.
"""
        result = parse_docstring(doc)
        assert_equal(result.returns, "Second return.")

    def test_multiple_args_sections_last_wins(self):
        doc = """\
Summary.

Args:
    x: First occurrence.

Args:
    y: Second occurrence.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"y": "Second occurrence."})


class TestArgsAndReturnsTogether(unittest.TestCase):

    def test_args_and_returns(self):
        doc = """\
Summary.

Args:
    name: The name.

Returns:
    The result.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(result.args, {"name": "The name."})
        assert_equal(result.returns, "The result.")

    def test_prose_before_sections_preserved(self):
        doc = """\
First line.

Longer description paragraph
spanning two lines.

Args:
    x: Something.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.doc,
            """\
First line.

Longer description paragraph
spanning two lines.""",
        )

    def test_returns_before_args(self):
        doc = """\
Summary.

Returns:
    The result.

Args:
    x: Something.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(result.args, {"x": "Something."})
        assert_equal(result.returns, "The result.")


class TestMalformedInput(unittest.TestCase):

    def test_section_header_with_no_entries(self):
        doc = """\
Summary.

Args:
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(result.args, {})
        assert_equal(result.returns, "")

    def test_section_header_not_at_line_start_is_prose(self):
        doc = """\
Summary.

    Args:
    name: value.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, doc.rstrip())
        assert_equal(result.args, {})

    def test_one_space_indented_line_not_parsed_as_arg(self):
        doc = """\
Summary.

Args:
 name: One-space indent.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {})

    def test_one_space_indented_line_in_section_body_ends_section(self):
        doc = """\
Summary.

Args:
    name:
        Some doc here.

 Something here, what happens now?
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"name": "Some doc here."})
        assert_equal(
            result.doc,
            """\
Summary.

 Something here, what happens now?""",
        )

    def test_two_space_indented_line_in_section_body_absorbed_into_arg_description(
        self,
    ):
        doc = """\
Summary.

Args:
    name:
        Some doc here.

  Something here, what happens now?
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "Some doc here.\n\nSomething here, what happens now?"},
        )
        assert_equal(result.doc, "Summary.")

    def test_url_in_arg_description_not_parsed_as_new_arg(self):
        doc = """\
Summary.

Args:
    name: See docs at
    https://example.com for details.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "See docs at https://example.com for details."},
        )
        assert_equal(result.doc, "Summary.")

    def test_tab_indented_header_is_prose_not_section(self):
        doc = """\
\tArgs:
\tname: value.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {})
        assert_equal(
            result.doc,
            """\
\tArgs:
\tname: value.""",
        )
        assert_equal(result.returns, "")

    def test_returns_with_no_content(self):
        doc = """\
Summary.

Returns:
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(result.args, {})
        assert_equal(result.returns, "")

    def test_never_raises_on_garbage_input(self):
        for bad in [
            "Args:\n    : no name.\n",
            "Args:\n    no_colon_here\n",
            "Returns:\n    \n    \n",
        ]:
            result = parse_docstring(bad)
            assert_equal(result, ParsedDocString(doc="", args={}, returns=""))

    def test_none_input_does_not_raise(self):
        result = parse_docstring(None)
        assert_equal(result, ParsedDocString(doc="", args={}, returns=""))

    def test_over_indented_arg_not_parsed(self):
        doc = """\
Summary.

Args:
     name: Five-space indent.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {})

    def test_args_section_with_no_summary(self):
        doc = "Args:\n    name: value.\n"
        result = parse_docstring(doc)
        assert_equal(result.doc, "")
        assert_equal(result.args, {"name": "value."})


class TestArgsTypeAnnotations(unittest.TestCase):

    def test_simple_type_annotation_stripped(self):
        doc = """\
Summary.

Args:
    name (str): The name to use.
"""
        result = parse_docstring(doc)
        assert_equal(result.doc, "Summary.")
        assert_equal(
            result.args,
            {"name": "The name to use."},
        )
        assert_equal(result.returns, "")

    def test_nested_parens_in_type_annotation_stripped(self):
        doc = """\
Summary.

Args:
    name (Union(int, str)): The name.
    other (Optional(str)): Optional value.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "The name.", "other": "Optional value."},
        )


class TestTwoSpaceIndent(unittest.TestCase):

    def test_two_space_indented_multiple_args(self):
        doc = """\
Summary.

Args:
  first: First argument.
  second: Second argument.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"first": "First argument.", "second": "Second argument."},
        )

    def test_two_space_indented_multiline_arg_continuation(self):
        doc = """\
Summary.

Args:
  name:   First line of description
    that continues here.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "First line of description that continues here."},
        )

    def test_two_space_indented_returns(self):
        doc = """\
Summary.

Returns:
  The result value.
"""
        result = parse_docstring(doc)
        assert_equal(result.returns, "The result value.")


class TestArgsStarredNames(unittest.TestCase):

    def test_mixed_regular_and_starred_args(self):
        doc = """\
Summary.

Args:
    name: The name.
    *args: Extra positional args.
    **kwargs: Extra keyword args.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {
                "name": "The name.",
                "args": "Extra positional args.",
                "kwargs": "Extra keyword args.",
            },
        )
        assert_equal(result.doc, "Summary.")


class TestRobotFrameworkVariableSyntax(unittest.TestCase):

    def test_mixed_rf_variable_syntax(self):
        doc = """\
Summary ${name} in doc.

Args:
    ${name}: The name
      with some extra spaces in the description.
    @{varargs}: Extra positional args.
    &{kwargs}: Extra keyword args.

    With some other lines in the description.
"""
        kwargs_doc = """\
Extra keyword args.

With some other lines in the description."""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {
                "name": "The name with some extra spaces in the description.",
                "varargs": "Extra positional args.",
                "kwargs": kwargs_doc,
            },
        )
        assert_equal(result.doc, "Summary ${name} in doc.")

    def test_empty_rf_variable_not_parsed_as_arg(self):
        for bad in ["${}:  desc", "@{}: desc", "&{}: desc"]:
            doc = f"Args:\n    {bad}\n"
            result = parse_docstring(doc)
            assert_equal(result.args, {}, msg=f"Expected no args for: {bad!r}")

    def test_list_and_dict_variables_with_spaces_in_name(self):
        doc = """\
Summary.

Args:
    @{my list}: The items.
    &{my  dict has spaces}: The mapping.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"my list": "The items.", "my  dict has spaces": "The mapping."},
        )

    def test_variable_with_only_spaces_is_ignored(self):
        doc = """\
Summary.

Args:
    ${   }: The value.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {})


class TestSpecialStrings(unittest.TestCase):

    def test_emoji_in_summary_passes_through(self):
        doc = "Does something useful 👨‍👩‍👦."
        result = parse_docstring(doc)
        assert_equal(result.doc, "Does something useful 👨‍👩‍👦.")

    def test_emoji_in_arg_description(self):
        doc = """\
Summary.

Args:
    mood: The current mood 😍.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"mood": "The current mood 😍."},
        )

    def test_fullwidth_colon_in_description_not_confused_with_arg_separator(self):
        doc = """\
Summary.

Args:
    name: Description with fullwidth colon：here.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.args,
            {"name": "Description with fullwidth colon\uff1ahere."},
        )


class TestReturnsCodeBlock(unittest.TestCase):

    def test_returns_with_blank_line_separated_code_block(self):
        doc = """\
Summary.

Returns:
    A dict mapping keys to the corresponding table row data
    fetched. For example:

    {b'Serak': ('Rigel VII', 'Preparer'),
     b'Zim': ('Irk', 'Invader')}

    Returned keys are always bytes.
"""
        result = parse_docstring(doc)
        expected = """\
A dict mapping keys to the corresponding table row data
fetched. For example:

{b'Serak': ('Rigel VII', 'Preparer'),
 b'Zim': ('Irk', 'Invader')}

Returned keys are always bytes."""
        assert_equal(result.returns, expected)

    def test_trailing_blank_lines_in_returns_stripped(self):
        doc = """\
Summary.

Returns:
    The result.


"""
        result = parse_docstring(doc)
        assert_equal(result.returns, "The result.")


class TestUnrecognisedSections(unittest.TestCase):

    def test_raises_section_preserved_in_doc_and_does_not_corrupt_args(self):
        doc = """\
Summary.

Args:
    x: Something.

Raises:
    ValueError: If bad.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"x": "Something."})
        assert_equal(
            result.doc,
            """\
Summary.

Raises:
    ValueError: If bad.""",
        )

    def test_custom_section_preserved_in_doc(self):
        doc = """\
Summary.

Note:
    This is an important note.

Returns:
    The result.
"""
        result = parse_docstring(doc)
        assert_equal(
            result.doc,
            """\
Summary.

Note:
    This is an important note.""",
        )
        assert_equal(result.returns, "The result.")

    def test_unrecognised_section_between_recognised_sections(self):
        doc = """\
Summary.

Args:
    x: Something.

Raises:
    ValueError: If bad.

Returns:
    The result.
"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"x": "Something."})
        assert_equal(result.returns, "The result.")
        assert_equal(
            result.doc,
            """\
Summary.

Raises:
    ValueError: If bad.""",
        )


class TestRobotFrameworkTags(unittest.TestCase):

    def test_tags_line_with_surrounding_prose_preserved(self):
        doc = """\
Summary line.

More details here.
Tags: tag1, tag2"""
        result = parse_docstring(doc)
        assert_equal(
            result,
            ParsedDocString(
                doc="""\
Summary line.

More details here.
Tags: tag1, tag2""",
                args={},
                returns="",
            ),
        )

    def test_tags_line_with_args_section(self):
        doc = """\
Summary line.

Args:
    x: The input.

Tags: kw1, kw2"""
        result = parse_docstring(doc)
        assert_equal(result.args, {"x": "The input."})
        assert_equal(result.returns, "")
        assert_equal(
            result.doc,
            """\
Summary line.

Tags: kw1, kw2""",
        )

    def test_tags_alone_on_line_is_unrecognised_section_body_goes_to_doc(self):
        doc = """\
Summary.

Tags:
    tag1    tag2"""
        result = parse_docstring(doc)
        assert_equal(result.args, {})
        assert_equal(result.returns, "")
        assert_equal(
            result.doc,
            """\
Summary.

Tags:
    tag1    tag2""",
        )


if __name__ == "__main__":
    # TODO: Add library that contains 10 000 keywords and see how performance is affected.
    unittest.main()
