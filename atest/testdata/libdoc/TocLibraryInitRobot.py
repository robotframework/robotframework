class TocLibraryInitRobot(object):
    """Simple library

    %TABLE_OF_CONTENTS%

    = 1 Heading =

    Some text here for chapter 1.

    = 2 Heading =

    Second chapter text there.

    Second paragraph.
    """

    def __init__(self, arg=None):
        """This library has init."""
        self.arg = arg

    def my_keyword(self):
        """Keyword documentation"""
        return self.arg
