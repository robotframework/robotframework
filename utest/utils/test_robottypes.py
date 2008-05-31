import unittest
import sys

if __name__ == "__main__":
    sys.path.insert(0,"../../../src")

from robot.errors import *
from robot.utils.asserts import *
from robot.utils.robottypes import *

lists = ( ["a","b","c"], ["a"], [], ("a","b"),("a",),() )
strings = ( "abc", "a", "" )
numbers = ( 123, 1, 0, -1, 0.0, 3.14 )
scalars = strings + numbers + ( None, unittest, {'a':1} )
    

class TestIsMethods(unittest.TestCase):    
    
    def test_is_list(self):
        for list in lists:
            assert_true(is_list(list), list)
        for scal in scalars:
            assert_false(is_list(scal), scal)
        
    def test_is_scalar(self):
        for scal in scalars:
            assert_true(is_scalar(scal), scal)
        for list in lists:
            assert_false(is_scalar(list), list)

    def test_is_str(self):
        for str in strings:
            assert_true(is_str(str), str)
        for nok in numbers + lists:
            assert_false(is_str(nok), nok)

    def test_is_number(self):
        assert is_number(1.1)
        assert is_number(0)
        assert is_number(4)
        assert is_number(-4)
        assert is_number(12387129387129837918273918723)

    def test_is_integer(self):
        assert is_integer(0)
        assert is_integer(4)
        assert is_integer(-4)
        assert is_integer(12387129387129837918273918723)
        assert not is_integer(1.1)
                    
    def test_to_boolean(self):
        true_items = [True, 1, 13, -12, 3.14, 'True', 'Yes', 't r u e']
        false_items = [False, 0, 0.00, 'No', 'False', 'falSE']
        extend_valid = ['Valid', 'Positive']
        extend_invalid = ['InValid', 'Negative']
        for item in true_items:
            assert_true(to_boolean(item), item)
        for item in extend_valid:
            assert_true(to_boolean(item, extend_valid), item)
        for item in false_items:
            assert_false(to_boolean(item), item)
        for item in extend_invalid:
            assert_false(to_boolean(item, None, extend_invalid), item)
            
    def test_to_boolean_default(self):
        assert_false(to_boolean('hello world!'))
        assert_false(to_boolean('hello world!', default=False))
        assert_true(to_boolean('hello world!', default=True))
        

if __name__ == "__main__":
    unittest.main()
