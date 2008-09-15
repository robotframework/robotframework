import unittest

from robot.errors import DataError 
from robot.output.abstractlogger import AbstractLogger


class MockFile:

    def __init__(self):
        self.closed = False
        self.messages = []
        self.string = ""

    def flush(self):
        pass

    def erase_data(self):
        self.messages = []
        self.string = ""

    def write(self, line):
        self.messages.append(line)
        self.string += line

    def close(self):
        self.closed = True

class SuiteMock:
    def __init__(self, name='', doc='', include=None, exclude=None, suites=None):
        self.name = name
        self.doc = doc
        self.include = include or []
        self.exclude = exclude or []
        self.suites = suites or []

class BasicMock:   
    def __init__(self, name='', doc='', tags=None):
        self.name = name
        self.doc = doc
        self.tags = tags or []

class StatisticsMock:
    
    def __init__(self, status='', message='', starttime='20051122 12:34:56.789',
                 endtime='20051122 12:34:56.789'):
        self.status = status
        self.message = message
        self.starttime = starttime
        self.endtime = endtime
        
        
class TestAbstractLogger(unittest.TestCase):
        
    def test_set_threshold_invalid(self):
        logger = AbstractLogger('trace')
        self.assertRaises(DataError, logger.set_level,'INVALID THRESHOLD') 
        
    def test_getattr_with_invalid(self):
        logger = AbstractLogger('trace')
        try:
            logger.invalid('message')
            raise AssertionError, 'AttributeError not raised'
        except AttributeError:
            pass

        
if __name__ == '__main__':
    unittest.main()
