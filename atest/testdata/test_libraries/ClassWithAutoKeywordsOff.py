from robot.api.deco import keyword


class InvalidGetattr:

    def __getattr__(self, item):
        if item == 'robot_name':
            raise ValueError('This goes through getattr() and hasattr().')
        raise AttributeError


class ClassWithAutoKeywordsOff:
    ROBOT_AUTO_KEYWORDS = False

    def public_method_is_not_keyword(self):
        raise RuntimeError('Should not be executed!')

    @keyword(name="Decorated Method Is Keyword")
    def decorated_method(self):
        print('Decorated methods are keywords.')

    def _private_method_is_not_keyword(self):
        raise RuntimeError('Should not be executed!')

    @keyword
    def _private_decorated_method_is_keyword(self):
        print('Decorated private methods are keywords.')

    invalid_getattr = InvalidGetattr()
