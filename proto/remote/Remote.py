import xmlrpclib


class Remote:
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, uri='http://localhost:8270'):
        if '://' not in uri:
            uri = 'http://' + uri
        self._library = xmlrpclib.Server(uri)  #.robotframework

    def get_keyword_names(self):
        # TODO: Support also getKeywordNames (and runKeyword etc.)
        return self._library.get_keyword_names()

    def get_keyword_arguments(self, name):
        # TODO: Handle errors
        return self._library.get_keyword_arguments(name)

 #   def get_keyword_documentation(self, name):
 #       return self._library.get_keyword_documentation(name)

    def run_keyword(self, name, args):
        try:
            result = self._library.run_keyword(name, args)
        except xmlrpclib.Fault, err:
            raise RuntimeError(err.faultString)
        print result['output']
        if result['status'] != 'PASS':
            raise AssertionError(result['message'])
        return result['return']
