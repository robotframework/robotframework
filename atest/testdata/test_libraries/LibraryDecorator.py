from robot.api.deco import keyword, library


@library(scope='TEST SUITE', version='1.2.3', method_disabler=False)
class LibraryDecorator(object):

    def __init__(self):
        self.invalid = 'This method is not a keyword.'

    def library_decorator_disables_public_methods(self):
        print(self.invalid)

    @keyword(name="Decorated Method Is Keyword")
    def decorated_method(self):
        print(self.invalid)
