from robot.api.deco import keyword, library


@library
class LibraryDecorator:

    def not_keyword(self):
        raise RuntimeError('Should not be executed!')

    @keyword
    def decorated_method_is_keyword(self):
        print('Decorated methods are keywords.')

    @staticmethod
    @keyword
    def decorated_static_method_is_keyword():
        print('Decorated static methods are keywords.')

    @classmethod
    @keyword
    def decorated_class_method_is_keyword(cls):
        print('Decorated class methods are keywords.')
