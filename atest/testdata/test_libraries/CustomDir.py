from robot.api.deco import keyword, library


@library
class CustomDir:

    def __dir__(self):
        return ['normal', 'via_getattr', 'via_getattr_invalid', 'non_existing']

    @keyword
    def normal(self, arg):
        print(arg.upper())

    def __getattr__(self, name):
        if name == 'via_getattr':
            @keyword
            def func(arg):
                print(arg.upper())
            return func
        if name == 'via_getattr_invalid':
            raise ValueError('This is invalid!')
        raise AttributeError(f'{name!r} does not exist.')
