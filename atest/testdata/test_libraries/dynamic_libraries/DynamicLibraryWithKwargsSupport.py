# TODO: Rename to DynamicLibraryWithInvalidArgSpec
# Also, run_keyword can just pass...
KEYWORDS = {
    'kwargs before positional args': (lambda a, *x: (a, x), ['**kwargs', 'a']),
    'kwargs before named args': (lambda a=1, *x: (a, x), ['**kwargs', 'a=1']),
    'kwargs before varargs': (lambda a=1, *x: (a, x), ['**kwargs', '*varargs']),
}

class DynamicLibraryWithKwargsSupport(object):

    def get_keyword_names(self):
        return sorted(KEYWORDS)

    def run_keyword(self, kw_name, args, kwargs):
        return KEYWORDS[kw_name][0](*args, **kwargs)

    def get_keyword_arguments(self, kw_name):
        return KEYWORDS[kw_name][1]
