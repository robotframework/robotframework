import sys, unittest
    
from robot.parsing.rawdata import *
from robot.utils.asserts import *


class _MockSyslog:
    pass

class TestTabularRawData(unittest.TestCase):
    
    def setUp(self):
        self.data = TabularRawData('tests.html', _MockSyslog())
                           
    def test_start_setting_table(self):
        for name in ['Setting',' set\nt\tings ',' META D A T A  ']:
            assert self.data.start_table(name), name
            assert self.data._table._data is self.data.settings, name
    
    def test_start_variable_table(self):
        for name in ['variable','Var I Able s']:
            assert self.data.start_table(name), name
            assert self.data._table._data is self.data.variables, name

    def test_start_testcase_table(self):
        for name in ['Test\tCase','       t e s t      \n\n\n      c a s e s ']:
            assert self.data.start_table(name), name
            assert self.data._table._data is self.data.testcases, name
    
    def test_start_testcase_table(self):
        for name in ['keyword','KEYWORDS','  User  Keyword  ','user\tkeywords']:
            assert self.data.start_table(name), name
            assert self.data._table._data is self.data.keywords, name

    def test_start_invalid_table(self):
        for name in ['My Setting','Variablez','Test']:
            assert not self.data.start_table(name), name
    
    def test_empty_type(self):
        assert_equals(self.data.get_type(), self.data.EMPTY)
        
    def test_resource_type(self):
        self.data.start_table('Settings')
        self.data.add_row(['Name','Test'])
        assert_equals(self.data.get_type(), self.data.RESOURCE)
        self.data.start_table('Variables')
        self.data.add_row(['${var}','foo'])
        assert_equals(self.data.get_type(), self.data.RESOURCE)
        self.data.start_table('Keywords')
        self.data.add_row(['My keyword','Noop'])
        assert_equals(self.data.get_type(), self.data.RESOURCE)
        
    def test_testcase_type(self):
        self.data.start_table('Test Cases')
        self.data.add_row(['My test','Noop'])
        assert_equals(self.data.get_type(), self.data.TESTCASE)
        self.data.start_table('Keywords')
        self.data.add_row(['My keyword','Noop'])
        assert_equals(self.data.get_type(), self.data.TESTCASE)
        
        
if __name__ == '__main__':
    unittest.main()
            
            
            