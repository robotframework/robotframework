from robot.api.deco import keyword


class DisablePublicMethods(object):

    ROBOT_AUTO_KEYWORDS = False

    def __init__(self):
        self.invalid = 'This method is not a keyword.'

    def public_method_is_not_keyword(self):
        print(self.invalid)

    @keyword(name="Decorated Method Is Keyword")
    def decorated_method(self):
        print('Decorated methods are keywords.')

    def _private_method_is_not_keyword(self):
        print(self.invalid)

    @keyword
    def _private_decorated_method_is_keyword(self):
        print('Decorated private methods are keywords.')
