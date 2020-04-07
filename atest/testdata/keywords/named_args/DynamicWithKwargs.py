from DynamicWithoutKwargs import DynamicWithoutKwargs


KEYWORDS = {
    'Kwargs': ['**kwargs'],
    'Args & Kwargs': ['a', 'b=default', ('c', 'xxx'), '**kwargs'],
    'Args, Varargs & Kwargs': ['a', 'b=default', '*varargs', '**kws'],
}


class DynamicWithKwargs(DynamicWithoutKwargs):

    def __init__(self):
        DynamicWithoutKwargs.__init__(self, **KEYWORDS)

    def run_keyword(self, name, args, kwargs):
        return self._pretty(*args, **kwargs)
