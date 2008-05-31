class _BaseLib:
    
    def __init__(self):
        self.registered = {}
    
    def register(self, name):
        self.registered[name] = None
    
    def should_be_registered(self, *expected):
        exp = dict([ (name, None) for name in expected ])
        if self.registered != exp:
            raise AssertionError, 'Wrong registered: %s != %s' \
                % (self.registered.keys(), exp.keys())


class Global(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'global'
    
class Suite(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
     
class Test(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'TeSt CAse'
    
class InvalidValue(_BaseLib):
    ROBOT_LIBRARY_SCOPE = 'invalid'
    
class InvalidEmpty(_BaseLib):
    pass

class InvalidMethod(_BaseLib):
    def ROBOT_LIBRARY_SCOPE(self):
        pass
    
class InvalidNone(_BaseLib):
    ROBOT_LIBRARY_SCOPE = None
