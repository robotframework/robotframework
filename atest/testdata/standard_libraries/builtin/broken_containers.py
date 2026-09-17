from collections.abc import Mapping, Sequence

__all__ = ["BROKEN_ITERABLE", "BROKEN_MAPPING", "BROKEN_SEQUENCE"]


class BrokenIterable:

    def __iter__(self):
        yield "x"
        raise ValueError(type(self).__name__)

    def __getitem__(self, item):
        return item

    def __len__(self):
        return 2


class BrokenSequence(BrokenIterable, Sequence):
    pass


class BrokenMapping(BrokenIterable, Mapping):
    pass


BROKEN_ITERABLE = BrokenIterable()
BROKEN_SEQUENCE = BrokenSequence()
BROKEN_MAPPING = BrokenMapping()
