import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer


class SimpleLibrary(SimpleXMLRPCServer):

    def __init__(self, port=8270):
        SimpleXMLRPCServer.__init__(self, ('localhost', int(port)))
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.stop_remote_server)
        self.serve_forever()

    def serve_forever(self):
        self._shutdown = False
        while not self._shutdown:
            self.handle_request()

    def stop_remote_server(self):
        self._shutdown = True
        return True

    def get_keyword_names(self):
        return ['kw_1', 'kw_2', 'stop_remote_server']

    def run_keyword(self, name, args):
        if name == 'kw_1':
            return {'status': 'PASS', 'return': ' '.join(args)}
        elif name == 'kw_2':
            return {'status': 'FAIL', 'error': ' '.join(args)}
        else:
            self.stop_remote_server()
            return {'status': 'PASS'}


if __name__ == '__main__':
    SimpleLibrary(*sys.argv[1:])
