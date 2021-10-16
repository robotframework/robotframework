ROBOT_LISTENER_API_VERSION = 2


class ListenerMethod:

    def __init__(self, name):
        self.__name__ = name
        self.failed = False

    def __call__(self, *args, **kws):
        if not self.failed:
            self.failed = True
            raise AssertionError("Expected failure in %s!" % self.__name__)


for name in ['start_suite', 'end_suite', 'start_test', 'end_test',
             'start_keyword', 'end_keyword', 'log_message', 'message',
             'output_file', 'log_file', 'report_file', 'debug_file', 'close']:
    globals()[name] = ListenerMethod(name)
