ROBOT_LIBRARY_DOC_FORMAT = "Markdown"


def arg_docs(own_line, multiline, *next_line, empty_doc, no_doc) -> str:
    """Example with *everything*!

    This is the second paragraph. We also have an indented
    example:

        keyword(1, 2, kwonly=3, extra=4)

    Args:
        own_line: Documentation on same line.
        multiline (ignored): Longer documentation that
            spans multiple lines.

                Indentation is preserved.

        next_line:
            Documentation on next line.
        empty_doc:

    Returns:
        Something useless.

        On multiple lines
                with indentation.

    Raises:
        ValueError: If something goes wrong.
        TypeError: Should *not* happen.

    The end.
    """
    return ""


def doc_for_not_existing_arg(not_set) -> int:
    """
    Arguments:
        not_set: Not set due to an error.
        non_existing: This causes that error.

    RETURNS: Zero
    """
    return 0
