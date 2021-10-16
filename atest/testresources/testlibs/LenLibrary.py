class LenLibrary:
    """Library with default zero __len__.

    Example:

    >>> l = LenLibrary()
    >>> assert not l
    >>> l.set_length(1)
    >>> assert l
    """
    def __init__(self):
        self._length = 0

    def __len__(self):
        return self._length

    def set_length(self, length):
        self._length = int(length)
