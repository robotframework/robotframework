from robot.api.deco import keyword, library


@library
class LibraryDecorator(object):

    def not_keyword(self):
        raise RuntimeError('Should not be executed!')

    @keyword
    def decorated_method_is_keyword(self):
        print('Decorated methods are keywords.')
