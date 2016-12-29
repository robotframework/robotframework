class DocFormat:
    """Library to test documentation formatting.

    *bold* or <b>bold</b> http://example.com
    """

    def keyword(self):
        """*bold* or <b>bold</b> http://example.com"""

    def link(self):
        """Link to `Keyword`."""

    def rest(self):
        """Let's see *how well* reST__ works.

        This documentation is mainly used for manually verifying reST output.
        This link to \\`Keyword\\` is also automatically tested.

        ====  =====
        My    table
        two   rows
        ====  =====

        - list
        - here

        Preformatted::

            def example():
                pass

        __ http://docutils.sourceforge.net

        .. code:: robotframework

            *** Test Cases ***
            Example
                Log    How cool is this!?!?!1!
        """
