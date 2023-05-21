class ObjectWithSetItemCap:
    def __init__(self) -> None:
        self._dict = {}

    def clear(self):
        self._dict = {}

    def __setitem__(self, item, value):
        self._dict[item] = value

    def __getitem__(self, item):
        return self._dict[item]

    @property
    def container(self):
        return self._dict

class ObjectWithoutSetItemCap:
    def __init__(self) -> None:
        pass

OBJECT_WITH_SETITEM_CAP = ObjectWithSetItemCap()
OBJECT_WITHOUT_SETITEM_CAP = ObjectWithoutSetItemCap()
