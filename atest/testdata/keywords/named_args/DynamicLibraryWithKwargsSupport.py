from DynamicLibrary import DynamicLibrary

KEYWORDS = {
    'Mandatory, Named And Kwargs': ['a', 'b=default', '**kwargs'],
    'Mandatory, Named, Varargs And Kwargs': ['a', 'b=default', '*varargs', '**kwargs'],
}


class DynamicLibraryWithKwargsSupport(DynamicLibrary):

    def __init__(self):
        DynamicLibrary.__init__(self, **KEYWORDS)

    def run_keyword(self, name, args, kwargs):
        return self._pretty(*args, **kwargs)
