import xmlrpclib


class RobotXmlRpc:
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, uri):
        if '://' not in uri:
            uri = 'http://' + uri
        self._lib = xmlrpclib.Server(uri).robot

    def get_keyword_names(self):
        return self._lib.get_keyword_names()

    def run_keyword(self, name, args):
        try:
            result = self._lib.run_keyword(name, args)
        except xmlrpclib.Fault, err:
            raise RuntimeError(err.faultString)
        print result['output']
        if result['status'] == 'PASS':
            return result['return']
        else:
            raise AssertionError(result['message'])
