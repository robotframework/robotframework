class _BaseLib:

    def __init__(self):
        self.registered = set()

    def register(self, name):
        self.registered.add(name)

    def should_be_registered(self, *expected):
        if self.registered != set(expected):
            raise AssertionError('Wrong registered: %s != %s'
                                 % (sorted(self.registered), sorted(expected)))


class Global(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'global'
    initializations = 0

    def __init__(self):
        Global.initializations += 1
        _BaseLib.__init__(self)

    def should_be_registered(self, *expected):
        if self.initializations != 1:
            raise AssertionError("Global library initialized more than once.")
        _BaseLib.should_be_registered(self, *expected)


class Suite(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'SUITE'


class TestSuite(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'


class Test(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'TeSt'


class TestCase(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'TeSt CAse'


class Task(_BaseLib):
    # Any non-recognized value is mapped to TEST scope.
    ROBOT_LIBRARY_SCOPE = 'TASK'


class InvalidValue(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'invalid'


class InvalidEmpty(_BaseLib):
    pass


class InvalidMethod(_BaseLib):
    def ROBOT_LIBRARY_SCOPE(self):
        pass


class InvalidNone(_BaseLib):
    ROBOT_LIBRARY_SCOPE = None
