from robot.api.deco import keyword, library


class Listener(object):
    ROBOT_LISTENER_API_VERSION = 3


@library(scope='TEST SUITE', version='1.2.3', listener=Listener())
class LibraryDecoratorWithArgs(object):

    def not_keyword_v2(self):
        raise RuntimeError('Should not be executed!')

    @keyword(name="Decorated method is keyword v.2")
    def decorated_method_is_keyword(self):
        print('Decorated methods are keywords.')
