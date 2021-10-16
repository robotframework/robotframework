class NewStyleClassLibrary:

    def mirror(self, arg):
        arg = list(arg)
        arg.reverse()
        return ''.join(arg)

    @property
    def property_getter(self):
        raise SystemExit('This should not be called, ever!!!')

    @property
    def _property_getter(self):
        raise SystemExit('This should not be called, ever!!!')


class NewStyleClassArgsLibrary:

    def __init__(self, param):
        self.get_param = lambda self: param


class MyMetaClass(type):

    def __new__(cls, name, bases, ns):
        ns['kw_created_by_metaclass'] = lambda self, arg: arg.upper()
        return type.__new__(cls, name, bases, ns)

    def method_in_metaclass(cls):
        pass


class MetaClassLibrary(metaclass=MyMetaClass):

    def greet(self, name):
        return 'Hello %s!' % name
