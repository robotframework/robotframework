class NewStyleClassLibrary(object):
    
    def mirror(self, arg):
        arg = list(arg)
        arg.reverse()
        return ''.join(arg)

    def _property_getter(self):
        raise SystemExit('This should not be called, ever!!!')
    
    prop = property(_property_getter)
    
    
class NewStyleClassArgsLibrary(object):
    
    def __init__(self, param):
        self.get_param = lambda self: param
    
    
class _MyMetaClass(type):
    
    def __new__(cls, name, bases, ns):
        ns['kw_created_by_metaclass'] = lambda self, arg: arg.upper()
        return type.__new__(cls, name, bases, ns)

    def method_in_metaclass(cls):
        pass


class MetaClassLibrary(object):
    __metaclass__ = _MyMetaClass

    def greet(self, name):
        return 'Hello %s!' % name
