from robot.api.deco import keyword, library


@library(scope='TEST SUITE', version='1.2.3')
class LibraryDecoratorWithArgs(object):

    def library_decorator_with_args_disables_public_methods(self):
        raise RuntimeError('Should not be executed!')

    @keyword(name="Decorated Method Is Keyword")
    def decorated_method(self):
        print('Decorated methods are keywords.')
