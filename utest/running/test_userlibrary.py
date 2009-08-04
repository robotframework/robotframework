import unittest
import sys
import os

from robot.parsing.userkeyword import UserHandlerList
from robot.running import userkeyword
from robot.errors import DataError
from robot.utils.asserts import *

    
class RawDataStub:
    
    RESOURCE = 2
    
    def __init__(self, source, *keyword_names):
        self.source = source
        self.keywords = [ KeywordDataStub(name) for name in keyword_names ]
        
    def get_type(self):
        return self.source == 'NOT_RESOURCE' and 1 or 2
    
        
class KeywordDataStub:
    
    def __init__(self, name):
        self.name = name
        self.keywords = []
        self.metadata = []
        self.reported_errors = []
        
    def report_invalid_syntax(self, error):
        self.reported_errors.append(error)


class UserHandlerStub:
    
    def __init__(self, kwdata, library):
        self.name = kwdata.name
        if kwdata.name == 'FAIL':
            raise Exception, 'Expected failure'


class EmbeddedArgsTemplateStub:
    
    def __init__(self, kwdata, library):
        self.name = kwdata.name
        if kwdata.name != 'Embedded ${arg}':
            raise TypeError


class TestUserLibrary(unittest.TestCase):

    def setUp(self):
        self._orig_userhandler = userkeyword.UserHandler
        self._orig_embeddedargstemplate = userkeyword.EmbeddedArgsTemplate
        userkeyword.UserHandler = UserHandlerStub
        userkeyword.EmbeddedArgsTemplate = EmbeddedArgsTemplateStub
        
    def tearDown(self):
        userkeyword.UserHandler = self._orig_userhandler
        userkeyword.EmbeddedArgsTemplate = self._orig_embeddedargstemplate
        
    def test_name_from_resource(self):
        for source, exp in [ ('resources.html', 'resources'), 
                             (os.path.join('..','res','My Res.HTM'), 'My Res'),
                             (os.path.abspath('my_res.xhtml'), 'my_res') ]:
            kwdata  = UserHandlerList(RawDataStub(source).keywords)
            lib = userkeyword.UserLibrary(kwdata, source)
            assert_equals(lib.name, exp)
            
    def test_name_from_test_case_file(self):
        assert_none(self._get_userlibrary('NOT_RESOURCE').name)
        
    def test_creating_keyword(self):
        lib = self._get_userlibrary('source', 'kw 1', 'kw 2')
        assert_equals(len(lib.handlers.keys()), 2)
        assert_true(lib.handlers.has_key('kw 1'))
        assert_true(lib.handlers.has_key('kw 2'))

    def test_creating_keyword_when_kw_name_has_embedded_arg(self):
        lib = self._get_userlibrary('source', 'Embedded ${arg}')
        self._lib_has_embedded_arg_keyword(lib)

    def test_creating_keywords_when_normal_and_embedded_arg_kws(self):
        lib = self._get_userlibrary('source', 'kw1', 'Embedded ${arg}', 'kw2')
        assert_equals(len(lib.handlers.keys()), 3)
        assert_true(lib.handlers.has_key('kw1'))
        assert_true(lib.handlers.has_key('kw 2'))
        self._lib_has_embedded_arg_keyword(lib)

    def test_creating_duplicate_embedded_arg_keyword_in_resource_file(self):
        lib = self._get_userlibrary('source', 'Embedded ${arg}', 
                                    'kw', 'Embedded ${arg}')
        assert_equals(len(lib.handlers.keys()), 2)
        assert_true(lib.handlers.has_key('kw'))
        assert_equals(lib.handlers['Embedded ${arg}']._error, 
                      "Keyword 'Embedded ${arg}' defined multiple times")
        assert_equals(lib.embedded_arg_handlers, [])

    def test_creating_duplicate_keyword_in_resource_file(self):
        lib = self._get_userlibrary('source', 'kw', 'kw', 'kw 2')
        assert_equals(len(lib.handlers.keys()), 2)
        assert_true(lib.handlers.has_key('kw'))
        assert_true(lib.handlers.has_key('kw 2'))
        assert_equals(lib.handlers['kw']._error, 
                      "Keyword 'Kw' defined multiple times")
        
    def test_creating_duplicate_keyword_in_test_case_file(self):
        lib = self._get_userlibrary('NOT_RESOURCE', 'MYKW', 'my kw')
        assert_equals(len(lib.handlers.keys()), 1)
        assert_true(lib.handlers.has_key('mykw'))
        assert_equals(lib.handlers['mykw']._error,
                      "Keyword 'My Kw' defined multiple times")

    def test_has_handler_with_non_existing_keyword(self):
        lib = self._get_userlibrary('source', 'kw')
        assert_false(lib.has_handler('non existing kw'))
        
    def test_has_handler_with_normal_keyword(self):
        lib = self._get_userlibrary('source', 'kw')
        assert_true(lib.has_handler('kw'))

    def test_get_handler_with_non_existing_keyword(self):
        lib = self._get_userlibrary('source', 'kw')
        err = "No keyword handler with name 'non existing' found"
        assert_raises_with_msg(DataError, err, lib.get_handler, 'non existing')

    def test_get_handler_with_normal_keyword(self):
        lib = self._get_userlibrary('source', 'kw')
        handler = lib.get_handler('kw')
        assert_equals(handler, lib.handlers['kw'])
        assert_true(isinstance(handler, UserHandlerStub))

    def _get_userlibrary(self, source, *keyword_names):
        kwdata = UserHandlerList(RawDataStub(source, *keyword_names).keywords)
        return userkeyword.UserLibrary(kwdata)
        
    def _lib_has_embedded_arg_keyword(self, lib):
        assert_true(lib.handlers.has_key('Embedded ${arg}'))
        assert_equals(len(lib.embedded_arg_handlers), 1)
        assert_equals(lib.embedded_arg_handlers[0].name, 'Embedded ${arg}')


if __name__ == '__main__':
    unittest.main()
