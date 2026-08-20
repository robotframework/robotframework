from robot.api.deco import library


@library(version="1.0", doc_format="MARKDOWN", auto_keywords=True)
class MarkdownLibrary:
    """Intro doc."""

    def __init__(self, arg: str = "default", other: int = 1):
        """Importing doc."""

    def positional_and_named(
        self,
        pos_only: str,
        /,
        normal: int = 1,
        *,
        named_only: str = "default",
    ) -> str:
        """Keyword doc.

        Args:
            pos_only: positional-only argument.
            normal: normal argument document.
                continues here.
            named_only: named-only argument.

        Returns:
            Always string.

        Raises:
            ValueError: Never
            TypeError: Not ever

        Tags:
            tag1, tag2
        """
        return ""

    def varargs_and_kwargs(self, *args: str, **kwargs: str):
        """Doc for variable arguments and keyword arguments.

        Args:
            *args (str): varargs doc.
            **kwargs (str): keyword args doc.
        """
