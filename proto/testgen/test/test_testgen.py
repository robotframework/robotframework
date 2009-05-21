import unittest
from StringIO import StringIO

from os.path import dirname, join
import sys
sys.path.insert(0, join(dirname(__file__), '..'))

from testgen import VariableIterator


class TestVariableIterator(unittest.TestCase):

    def test_creation(self):
        vars = VariableIterator(StringIO('* variables *\n${var1}\t${var2}\nval1\tval2\n'))
        self.assertEqual(vars._variable_mapping, {'${var1}': 0, '${var2}': 1})

    def test_iteration(self):
        vars = VariableIterator(StringIO('* variables *\n${var1}\t${var2}\nval1.1\tval2.1\nval1.2\tval2.2\n'))
        for var, exp in zip(vars, [{'${var1}': 'val1.1', '${var2}': 'val2.1'}, {'${var1}': 'val1.2', '${var2}': 'val2.2'}]):
            self.assertEqual(var, exp)
    

if __name__ == '__main__':
    unittest.main()
