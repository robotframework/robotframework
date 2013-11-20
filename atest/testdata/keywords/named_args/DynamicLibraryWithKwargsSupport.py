from dynamic_library_impl import var_args
from DynamicLibrary import DynamicLibrary

KEYWORDS = {
    'Mandatory, Named And Kwargs': (var_args, ['a', 'b=default', '**kwargs']),
    'Mandatory, Named, Varargs And Kwargs': (var_args, ['a', 'b=default', '*varargs', '**kwargs']),
}


class DynamicLibraryWithKwargsSupport(DynamicLibrary):

    def __init__(self):
        DynamicLibrary.__init__(self, **KEYWORDS)

    def run_keyword(self, name, args, kwargs):
        return self.keywords[name][0](*args, **kwargs)
