import sys
import unittest
from StringIO import StringIO

if __name__ == "__main__":
    sys.path.insert(0, "../../../src")
    
from robot.parsing.tsvreader import TsvReader
from robot.utils.asserts import *


class MockRawData:
    def __init__(self, processed_tables=None):
        self.tables = {}
        self._current = None
        self._processed = processed_tables
    
    def start_table(self, name):
        if self._processed is not None and name not in self._processed:
            return False
        self.tables[name] = []
        self._current = name
        return True
    
    def add_row(self, cells):
        self.tables[self._current].append(cells)
    

class TestTsvParser(unittest.TestCase):
    
    def test_start_table(self):
        tsv = StringIO('''*Setting*\t*Value*\t*V*
Some data here
***Variable

*Not*Table*

Keyword*\tNot a table because doesn't start with '*'

*******************T*e*s*t*********C*a*s*e************\t***********\t******\t*
''')
        data = MockRawData(['Setting','Variable','TestCase','Keyword'])
        TsvReader().read(tsv, data)
        act = data.tables.keys()
        act.sort()
        assert_equals(act, ['Setting','TestCase','Variable'])
        
    def test_rows(self):
        tsv = StringIO('''Ignored text before tables...
Mote\tignored\text
*Setting*\t*Value*\t*Value*
Document\tWhatever\t\t\\\t
Default Tags\tt1\tt2\tt3\t\t

*Variable*\tWhatever
  2 spaces before and after  
\\ \\ 2 escaped spaces before and after \\ \\
4 spaces in the row below
    
''')
        data = MockRawData()
        TsvReader().read(tsv, data)
        expected1 = [ ['Document','Whatever','','\\'],
                      ['Default Tags','t1','t2','t3'],
                      [''] ]
        expected2 = [ ['  2 spaces before and after'], 
                      ['\\ \\ 2 escaped spaces before and after \\ \\'], 
                      ['4 spaces in the row below'], 
                      [''] ]
        assert_equals(len(data.tables.keys()), 2)
        self._verify_rows(data.tables['Setting'], expected1)
        self._verify_rows(data.tables['Variable'], expected2)

    def _verify_rows(self, actual, expected):
        assert_equals(len(actual), len(expected))
        for act, exp in zip(actual, expected):
            assert_equals(act, exp)
    
    def test_quotes(self):
        tsv = StringIO('''*Variable*\t*Value*
${v}\tHello
${v}\t"Hello"
${v}\t"""Hello"""
${v}\t"""""Hello"""""
${v}\t"Hel""lo"
${v}\t"""Hel "" """" lo"""""""
${v}\t"Hello
${v}\tHello"
''')
        data = MockRawData()
        TsvReader().read(tsv, data)
        actual = [ row for row in data.tables['Variable'] ]
        expected = ['Hello','Hello','"Hello"','""Hello""','Hel"lo',
                    '"Hel " "" lo"""','"Hello','Hello"']
        assert_equals(len(actual), len(expected))
        for act, exp in zip(actual, expected):
            assert_equals(act[0], '${v}')
            assert_equals(act[1], exp)

        
if __name__ == '__main__':
    unittest.main()
