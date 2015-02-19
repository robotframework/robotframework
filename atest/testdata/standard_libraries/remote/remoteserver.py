import inspect
import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer


class RemoteServer(SimpleXMLRPCServer):

    def __init__(self, library, port=8270, port_file=None):
        SimpleXMLRPCServer.__init__(self, ('127.0.0.1', int(port)))
        self.library = library
        self._shutdown = False
        self.register_function(self.get_keyword_names)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.run_keyword)
        announce_port(self.socket, port_file)
        self.serve_forever()

    def serve_forever(self):
        while not self._shutdown:
            self.handle_request()

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
        except AssertionError as err:
            return {'status': 'FAIL', 'error': str(err)}
        else:
            return {'status': 'PASS',
                    'return': result if result is not None else ''}


class DirectResultRemoteServer(RemoteServer):

    def run_keyword(self, name, args, kwargs=None):
        try:
            return getattr(self.library, name)(*args, **(kwargs or {}))
        except SystemExit:
            self._shutdown = True
            return {'status': 'PASS'}


def announce_port(socket, port_file=None):
    port = socket.getsockname()[1]
    sys.stdout.write('Remote server starting on port %s.\n' % port)
    sys.stdout.flush()
    if port_file:
        with open(port_file, 'w') as f:
            f.write(str(port))
