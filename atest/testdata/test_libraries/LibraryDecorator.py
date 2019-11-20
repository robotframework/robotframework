from robot.api.deco import keyword, library

@library
class LibraryDecorator(object):

    def library_decorator_disables_public_methods(self):
        raise RuntimeError('Should not be executed!')

    @keyword(name="Method From Library Decorator")
    def decorated_method(self):
        print('Decorated methods are keywords.')