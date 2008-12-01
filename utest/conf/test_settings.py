import unittest
import os

from robot.conf.settings import _BaseSettings
from robot.utils.asserts import assert_equals


class SettingWrapper(_BaseSettings):
    
    def __init__(self):
        pass


class TestSplitArgsFromName(unittest.TestCase):
    
    def setUp(self):
        self.method = SettingWrapper()._split_args_from_name
        
    def test_with_no_args(self):
        assert_equals(self.method('name'), ('name', []))
        
    def test_with_args(self):
        assert_equals(self.method('name:arg'), ('name', ['arg']))
        assert_equals(self.method('listener:v1:v2:v3'), ('listener', ['v1', 'v2', 'v3']))
        assert_equals(self.method('a:b:c'), ('a', ['b', 'c']))
        
    def test_empty_args(self):
        assert_equals(self.method('foo:'), ('foo', ['']))
        assert_equals(self.method('bar:arg1::arg3'), ('bar', ['arg1', '', 'arg3']))
        assert_equals(self.method('L:'), ('L', ['']))
        
    def test_with_windows_path_without_args(self):
        assert_equals(self.method('C:\\name.py'), ('C:\\name.py', []))
        assert_equals(self.method('X:\\APPS\\listener'), ('X:\\APPS\\listener', []))
        assert_equals(self.method('C:/varz.py'), ('C:/varz.py', []))
    
    def test_with_windows_path_with_args(self):
        assert_equals(self.method('C:\\name.py:arg1'), ('C:\\name.py', ['arg1']))
        assert_equals(self.method('D:\\APPS\\listener:v1:b2:z3'), 
                      ('D:\\APPS\\listener', ['v1', 'b2', 'z3']))   
        assert_equals(self.method('C:/varz.py:arg'), ('C:/varz.py', ['arg']))

    def test_existing_path_with_colons(self):
        # Colons aren't allowed in Windows paths (other than in "c:")
        if os.sep == '\\':
            return
        path = 'robot:framework:test:1:2:42'
        try:
            os.mkdir(path)
            assert_equals(self.method(path), (path, []))
        finally:
            os.rmdir(path)


if __name__ == '__main__':
    unittest.main()
