class DynamicLibraryWithoutArgspec:

    def get_keyword_names(self):
        return [name for name in dir(self) if name.startswith('do_')]

    def run_keyword(self, name, args):
        return getattr(self, name)(*args)

    def do_something(self, x):
        print(x)

    def do_something_else(self, x, y=0):
        print('x: %s, y: %s' % (x, y))

    def do_something_third(self, a, b=2, c=3):
        print(a, b, c)
