from robot.api.deco import keyword

ROBOT_AUTO_KEYWORDS = False


def public_method_is_not_keyword():
    raise RuntimeError('Should not be executed!')


@keyword(name="Decorated Method In Module Is Keyword")
def decorated_method():
    print('Decorated methods are keywords.')


def _private_method_is_not_keyword():
    raise RuntimeError('Should not be executed!')


@keyword
def _private_decorated_method_in_module_is_keyword():
    print('Decorated private methods are keywords.')
