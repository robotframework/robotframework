from collections import OrderedDict


class StatusDict(OrderedDict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if not key.startswith('_OrderedDict__'):
            self[key] = value
        else:
            OrderedDict.__setattr__(self, key, value)


Status = StatusDict(
    {
        'PASS': 'PASS',
        'FAIL': 'FAIL',
        'NOT_RUN': 'NOT_RUN',
        'SKIP': 'SKIP'
    }
)
