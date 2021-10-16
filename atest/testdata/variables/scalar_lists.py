LIST = ['spam', 'eggs', 21]


class _Extended:
    list = LIST
    string = 'not a list'
    def __getitem__(self, item):
        return LIST

EXTENDED = _Extended()


class _Iterable:
    def __iter__(self):
        return iter(LIST)

ITERABLE = _Iterable()
