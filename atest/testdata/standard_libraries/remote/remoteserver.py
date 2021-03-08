import inspect
import sys
from xmlrpc.server import SimpleXMLRPCServer


# Re-implementation of `robot.api.deco.keyword`. Cannot use the real thing
# because `robot` may not installed on this interpreter.
def keyword(name=None, tags=(), types=()):
    if callable(name):
        return keyword()(name)
    def deco(func):
        func.robot_name = name
        func.robot_tags = tags
        func.robot_types = types
        return func
    return deco


class RemoteServer(SimpleXMLRPCServer):

    def __init__(self, library, port=8270, port_file=None):
        SimpleXMLRPCServer.__init__(self, ('127.0.0.1', int(port)))
        self.library = library
        self._shutdown = False
        self._register_functions()
        announce_port(self.socket, port_file)
        self.serve_forever()

    def _register_functions(self):
        self.register_function(self.get_keyword_names)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.get_keyword_tags)
        self.register_function(self.get_keyword_documentation)
        self.register_function(self.run_keyword)

    def serve_forever(self):
        while not self._shutdown:
            self.handle_request()

    def get_keyword_names(self):
        return [attr for attr in dir(self.library) if attr[0] != '_']

    def get_keyword_arguments(self, name):
        kw = getattr(self.library, name)
        args, varargs, kwargs, defaults, kwoargs, kwodefaults, _ \
            = inspect.getfullargspec(kw)
        args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += [f'{n}={d}' for n, d in zip(names, defaults)]
        if varargs:
            args.append(f'*{varargs}')
        if kwoargs:
            if not varargs:
                args.append('*')
            args += [self._format_kwo(arg, kwodefaults) for arg in kwoargs]
        if kwargs:
            args.append(f'**{kwargs}')
        return args

    def _format_kwo(self, arg, defaults):
        if defaults and arg in defaults:
            return f'{arg}={defaults[arg]}'
        return arg

    def get_keyword_tags(self, name):
        kw = getattr(self.library, name)
        return getattr(kw, 'robot_tags', [])

    def get_keyword_documentation(self, name):
        kw = getattr(self.library, name)
        return inspect.getdoc(kw) or ''

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
    sys.stdout.write(f'Remote server starting on port {port}.\n')
    sys.stdout.flush()
    if port_file:
        with open(port_file, 'w') as f:
            f.write(str(port))
