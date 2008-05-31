import unittest
import sys

from robot.parsing.metadata import *
from robot.errors import *
from robot import utils
from robot.utils.asserts import *


suite_names = ('Documentation','TestSetup','TestTeardown','SuiteSetup',
               'SuiteTeardown','DefaultTags','ForceTags')
tc_names = ('Documentation','Setup','Teardown','Tags') 
uk_names = ('Documentation','Arguments','Return')


class _MockItem:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def extend(self, value):
        self.value.extend(value)

def _is_string_name(name):
    return utils.eq_any(name, ['Documentation'])

def test_initial(meta, names):
    for name in names:
        assert_equal(meta.get(name), None)
    
def test_set(meta, names):
    for name in names:
        if _is_string_name(name):
            test_set_string(meta, name)
        else:
            test_set_list(meta, name)

def test_set_string(meta, name):
    meta.set(_MockItem(name, ['hello']))
    assert_equal(meta.get(name), 'hello')
    meta.set(_MockItem(name, ['world']))
    assert_equal(meta.get(name), 'hello world')
    meta.set(_MockItem(name, ['and','hi','tellus']))
    assert_equal(meta.get(name), 'hello world and hi tellus')
    
    
def test_set_list(meta, name):
    meta.set(_MockItem(name, ['hello','again']))
    assert_equal(['hello','again'], meta.get(name))
    meta.set(_MockItem(name, ['world']))
    assert_equal(['hello','again','world'], meta.get(name))
    

class TestTestCaseMetadata(unittest.TestCase):
    
    def setUp(self):
        self.meta = TestCaseMetadata()
    
    def test_initial(self):
        test_initial(self.meta, tc_names)
        
    def test_set(self):
        test_set(self.meta, tc_names)
    

class TestUserKeywordMetadata(unittest.TestCase):
    
    def setUp(self):
        self.meta = UserKeywordMetadata()
        
    def test_initial(self):
        test_initial(self.meta, uk_names)
        
    def test_set(self):
        test_set(self.meta, uk_names)
    
    
class TestTestSuiteMetadata(unittest.TestCase):
    
    def setUp(self):
        self.meta = TestSuiteMetadata()
        
    def test_initial(self):
        test_initial(self.meta, suite_names)
        
    def test_set(self):
        test_set(self.meta, suite_names)

    

if __name__ == '__main__':
    unittest.main()
    