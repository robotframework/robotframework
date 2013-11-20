# TODO: Move code to run_keyword

KEYWORDS = {
    'argspec with other than strings': (lambda a, *x: (a, x), [1, 2]),
    'varargs before positional args': (lambda a, *x: (a, x), ['*varargs', 'a']),
    'varargs before named args': (lambda a=1, *x: (a, x), ['*varargs', 'a=1']),
    'named args before positional': (lambda a, b: (a, b), ['a=1', 'b']),
    'method': (lambda a: a, ['a'])
}

class DynamicLibrary(object):

    def get_keyword_names(self):
        return sorted(KEYWORDS)

    def run_keyword(self, kw_name, args):
        KEYWORDS[kw_name][0](*args)

    def get_keyword_arguments(self, kw_name):
        return KEYWORDS[kw_name][1]
