from collections.abc import Mapping


class MyObject:

    def __init__(self, name='<MyObject>'):
        self.name = name

    def __str__(self):
        return self.name


class MyMapping(Mapping):

    def __init__(self, data=None, **extra):
        self.data = data or {}
        self.data.update(extra)

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)
