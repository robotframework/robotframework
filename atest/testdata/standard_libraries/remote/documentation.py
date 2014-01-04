import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer

from remoteserver import announce_port


class Documentation(SimpleXMLRPCServer):

    def __init__(self, port=8270, port_file=None):
        SimpleXMLRPCServer.__init__(self, ('127.0.0.1', int(port)))
        self.register_function(self.get_keyword_names)
        self.register_function(self.get_keyword_documentation)
        self.register_function(self.run_keyword)
        announce_port(self.socket, port_file)
        self.serve_forever()

    def get_keyword_names(self):
        return ['Empty', 'Single line', 'Multi line']

    def get_keyword_documentation(self, name):
        if name == 'Single line':
            return 'Single line documentation'
        if name == 'Multi line':
            return 'Multi\nline\ndocumentation\n'
        return ''

    def run_keyword(self, name, args):
        return {'status': 'PASS'}


if __name__ == '__main__':
    Documentation(*sys.argv[1:])
