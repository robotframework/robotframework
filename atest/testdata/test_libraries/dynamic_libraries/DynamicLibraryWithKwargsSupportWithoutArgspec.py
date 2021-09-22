from DynamicLibraryWithoutArgspec import DynamicLibraryWithoutArgspec


class DynamicLibraryWithKwargsSupportWithoutArgspec(DynamicLibraryWithoutArgspec):

    def run_keyword(self, name, args, kwargs):
        return getattr(self, name)(*args, **kwargs)

    def do_something_with_kwargs(self, a, b=2, c=3, **kwargs):
        print(a, b, c, ' '.join('%s:%s' % (k, v) for k, v in kwargs.items()))
