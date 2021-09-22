def get_variables():
    return {'MIXED USAGE': MixedUsage()}


class MixedUsage:

    def __init__(self):
        self.data = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

    def __getitem__(self, item):
        if isinstance(item, slice) and item.start is item.stop is item.step is None:
            return self
        if isinstance(item, (int, slice)):
            return self.data[item]
        if isinstance(item, str):
            return self.data.index(item)
        raise TypeError
