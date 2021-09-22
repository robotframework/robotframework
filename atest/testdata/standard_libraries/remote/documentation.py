import sys
from xmlrpc.server import SimpleXMLRPCServer

from remoteserver import announce_port


class Documentation(SimpleXMLRPCServer):

    def __init__(self, port=8270, port_file=None):
        SimpleXMLRPCServer.__init__(self, ('127.0.0.1', int(port)))
        self.register_function(self.get_keyword_names)
        self.register_function(self.get_keyword_documentation)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.run_keyword)
        announce_port(self.socket, port_file)
        self.serve_forever()

    def get_keyword_names(self):
        return ['Empty', 'Single', 'Multi', 'Nön-ÄSCII']

    def get_keyword_documentation(self, name):
        return {'__intro__': 'Remote library for documentation testing purposes',
                'Empty': '',
                'Single': 'Single line documentation',
                'Multi': 'Short doc\nin two lines.\n\nDoc body\nin\nthree.',
                'Nön-ÄSCII': 'Nön-ÄSCII documentation'}.get(name)

    def get_keyword_arguments(self, name):
        return {'Empty': (),
                'Single': ['arg'],
                'Multi': ['a1', 'a2=d', '*varargs']}.get(name)

    def run_keyword(self, name, args):
        return {'status': 'PASS'}


if __name__ == '__main__':
    Documentation(*sys.argv[1:])
