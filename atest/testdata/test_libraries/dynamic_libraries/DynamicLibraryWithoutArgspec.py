# TODO: Move actual code to run_keyword
def do_something(x):
    print x

def do_something_else(x, y=0):
    print 'x: %s, y: %s' % (x, y)

def do_something_third(a, b=2, c=3):
    print a, b, c

KEYWORDS = {
    'do_something': do_something,
    'do_something_else': do_something_else,
    'do_something_third': do_something_third
}

class DynamicLibraryWithoutArgspec(object):
    def get_keyword_names(self):
        return KEYWORDS.keys()

    def run_keyword(self, kw_name, args):
        KEYWORDS[kw_name](*args)
