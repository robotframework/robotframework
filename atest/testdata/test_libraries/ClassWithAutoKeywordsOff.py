from robot.api.deco import keyword


class ClassWithAutoKeywordsOff(object):
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
