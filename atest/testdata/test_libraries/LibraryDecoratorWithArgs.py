from robot.api.deco import keyword, library


@library(scope='SUITE', version='1.2.3', listener='self')
class LibraryDecoratorWithArgs:
    start_suite_called = start_test_called = start_library_keyword_called = False

    @keyword(name="Decorated method is keyword v.2")
    def decorated_method_is_keyword(self):
        if not (self.start_suite_called and
                self.start_test_called and
                self.start_library_keyword_called):
            raise AssertionError('Listener methods are not called correctly!')
        print('Decorated methods are keywords.')

    def not_keyword_v2(self):
        raise RuntimeError('Should not be executed!')

    def start_suite(self, data, result):
        self.start_suite_called = True

    def start_test(self, data, result):
        self.start_test_called = True

    def start_library_keyword(self, data, impl, result):
        self.start_library_keyword_called = True
