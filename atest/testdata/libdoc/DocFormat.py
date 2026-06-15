class DocFormat:
    """Library to test documentation formatting.

    *bold* or <b>bold</b> http://example.com
    """

    def keyword(self):
        """*bold* or <b>bold</b> http://example.com"""

    def link(self):
        """Link to `Keyword` or not?"""

    def rest(self):
        """Let's see *how well* reST__ works.

        This documentation is mainly used for manually verifying reST output.
        This link to \\`Keyword\\` is also automatically tested.

        =====  =====
        Table  with
        two    rows
        =====  =====

        - list
        - here

        Preformatted::

            def example():
                pass

        Code:

        .. code:: robotframework

            *** Test Cases ***
            Example
                Log    How cool is this!?!?!1!

        __ http://docutils.sourceforge.net
        """

    def markdown(self):
        """Let's see *how well* [Markdown] works.

        This documentation is mainly used for manually verifying Markdown output.
        This link to [Keyword] is also automatically tested.

        Mandatory | Headers
        ----------| -------
        Table     | with
        two normal| rows

        - list
        - here

        Preformatted:

            def example():
                pass

        Code:

        ```robotframework
        *** Test Cases ***
        Example
            Log    How cool is this!?!?!1!
        ```

        [Markdown]: https://en.wikipedia.org/wiki/Markdown
        """
