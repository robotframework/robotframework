def keyword(arg, *, kwonly, **kwargs) -> str:
    """Keyword with different argument and docstring.

    This is second paragraph.

    Args:
        arg: Documentation at same line
        kwonly: With a long description that
            spans multiple lines

            def keyword(arg, *, kwonly, **kwargs) -> str:
                pass
        kwargs:
            Documentation at next line

    Here is more text in the docstring after the argument.

    Returns:
        This documentation for the return value

    This ends the docstring.
    """

    return "This is a return value."


def keyword_doc_not_existing_args(no_doc, other):
    """Doc

    Args:
        no_doc:
        other: Documentation for argument that does exist
        does_not_exist: Documentation for argument that does not exist
    """
    return "This is a return value."