import inspect
from SimpleXMLRPCServer import SimpleXMLRPCServer


class RemoteServer(SimpleXMLRPCServer):

    def __init__(self, library, port=8270):
        SimpleXMLRPCServer.__init__(self, ('127.0.0.1', int(port)))
        self.library = library
        self.register_function(self.get_keyword_names)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.run_keyword)
        self.serve_forever()

    def get_keyword_names(self):
        return [attr for attr in dir(self.library) if attr[0] != '_']

    def get_keyword_arguments(self, name):
        kw = getattr(self.library, name)
        args, varargs, kwargs, defaults = inspect.getargspec(kw)
        args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += ['%s=%s' % (n, d) for n, d in zip(names, defaults)]
        if varargs:
            args.append('*%s' % varargs)
        if kwargs:
            args.append('**%s' % kwargs)
        return args

    def run_keyword(self, name, args, kwargs=None):
        try:
            result = getattr(self.library, name)(*args, **(kwargs or {}))
        except AssertionError, err:
            return {'status': 'FAIL', 'error': str(err)}
        else:
            return {'status': 'PASS',
                    'return': result if result is not None else ''}
