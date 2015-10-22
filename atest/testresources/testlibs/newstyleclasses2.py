class MyMetaClass(type):

    def __new__(cls, name, bases, ns):
        ns['kw_created_by_metaclass'] = lambda self, arg: arg.upper()
        return type.__new__(cls, name, bases, ns)

    def method_in_metaclass(cls):
        pass


class MetaClassLibrary(object):
    __metaclass__ = MyMetaClass

    def greet(self, name):
        return 'Hello %s!' % name
