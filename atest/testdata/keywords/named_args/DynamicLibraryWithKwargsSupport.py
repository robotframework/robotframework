from dynamic_library_impl import var_args, return_argument, return_arguments
from DynamicLibrary import KEYWORDS, DynamicLibrary

KEYWORDS.update({
    'Mandatory, Named And Kwargs': (var_args, ['a', 'b=default', '**kwargs']),
    'Mandatory, Named, Varargs And Kwargs': (var_args, ['a', 'b=default', '*varargs', '**kwargs']),
})

class DynamicLibraryWithKwargsSupport(DynamicLibrary):

    def run_keyword(self, kw_name, args, kwargs):
        return KEYWORDS[kw_name][0](*args, **kwargs)
