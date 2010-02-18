import unittest

from robot.output.readers import _BaseReader
from robot.utils import DomWrapper
from robot.utils.asserts import assert_equals


data = '''<?xml version="1.0" encoding="UTF-8"?>
<suite>
</suite>
'''

class TestBaseReader(unittest.TestCase):

    def test_missing_statistics_tag(self):
        reader = _BaseReader(DomWrapper(string=data))
        assert_equals(reader.status, 'FAIL')
        assert_equals(reader.starttime, 'N/A')
        assert_equals(reader.endtime, 'N/A')
        assert_equals(reader.message, 'Broken output file')


if __name__ == '__main__':
    unittest.main()
