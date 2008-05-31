import unittest
import sys
import os

from robot.parsing.userkeyword import UserHandlerList
from robot.running import userkeyword
from robot.utils.asserts import *

    
class RawDataMock:
    
    RESOURCE = 2
    
    def __init__(self, source, *keyword_names):
        self.source = source
        self.keywords = [ KeywordDataMock(name) for name in keyword_names ]
        
    def get_type(self):
        return self.source == 'NOT_RESOURCE' and 1 or 2
    
        
class KeywordDataMock:
    
    def __init__(self, name):
        self.name = name
        self.keywords = []
        self.metadata = []
        self.reported_errors = []
        
    def report_invalid_syntax(self, error):
        self.reported_errors.append(error)


class UserHandlerMock:
    
    def __init__(self, kwdata, library):
        self.name = kwdata.name
        if kwdata.name == 'FAIL':
            raise Exception, 'Expected failure'
                

class TestUserLibrary(unittest.TestCase):

    def setUp(self):
        self._orig_userhandler = userkeyword.UserHandler
        userkeyword.UserHandler = UserHandlerMock
        
    def tearDown(self):
        userkeyword.UserHandler = self._orig_userhandler
        
    def test_name_from_resource(self):
        for source, exp in [ ('resources.html', 'resources'), 
                             (os.path.join('..','res','My Res.HTM'), 'My Res'),
                             (os.path.abspath('my_res.xhtml'), 'my_res') ]:
            kwdata  = UserHandlerList(RawDataMock(source).keywords)
            lib = userkeyword.UserLibrary(kwdata, source)
            assert_equals(lib.name, exp)
            
    def test_name_from_test_case_file(self):
        kwdata = UserHandlerList(RawDataMock('NOT_RESOURCE').keywords)
        lib = userkeyword.UserLibrary(kwdata)
        assert_none(lib.name)
        
    def test_creating_keyword(self):
        kwdata = UserHandlerList(RawDataMock('source', 'kw 1', 'kw 2').keywords)
        lib = userkeyword.UserLibrary(kwdata)
        assert_equals(len(lib.handlers.keys()), 2)
        assert_true(lib.handlers.has_key('kw 1'))
        assert_true(lib.handlers.has_key('kw 2'))
        
    def test_creating_duplicate_keyword_in_resource_file(self):
        kwdata = UserHandlerList(RawDataMock('source', 'kw', 'kw', 'kw 2').keywords)
        lib = userkeyword.UserLibrary(kwdata)
        assert_equals(len(lib.handlers.keys()), 2)
        assert_true(lib.handlers.has_key('kw'))
        assert_true(lib.handlers.has_key('kw 2'))
        err = "Keyword 'Kw' defined multiple times"
        assert_equals(lib.handlers['kw']._error, err)
        
    def test_creating_duplicate_keyword_in_test_case_file(self):
        kwdata = UserHandlerList(RawDataMock('NOT_RESOURCE', 'MYKW', 'my kw').keywords)
        lib = userkeyword.UserLibrary(kwdata)
        assert_equals(len(lib.handlers.keys()), 1)
        assert_true(lib.handlers.has_key('mykw'))
        err = "Keyword 'My Kw' defined multiple times"
        assert_equals(lib.handlers['mykw']._error, err)


if __name__ == '__main__':
    unittest.main()
