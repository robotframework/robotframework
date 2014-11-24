class DynamicLibraryWithoutGetKwArgsAndDoc:
    """Library doc set in class."""

    def __init__(self, doc=None):
        """Static __init__ doc."""
        if doc:
            self.__doc__ = doc

    def get_keyword_names(self):
        return ['Keyword']

    def run_keyword(self, name, args):
        pass
