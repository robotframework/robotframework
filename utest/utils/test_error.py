import unittest

from robot.utils.asserts import *
from robot import utils
if utils.is_jython:
    import JavaExceptions
    java_exceptions = JavaExceptions()

from robot.utils.error import get_error_details, get_error_message



class TestError(unittest.TestCase):
    
    def test_get_error_details_python(self):
        for exception, msg, exp_msg in [
                    (AssertionError, 'My Error', 'My Error'),
                    (AssertionError, None, 'AssertionError'),
                    (Exception, 'Another Error', 'Another Error'),
                    (Exception, None, 'Exception'),
                    (ValueError, 'Something', 'ValueError: Something'), 
                    (ValueError, None, 'ValueError'),
                    (AssertionError, 'Msg\nin 3\nlines', 'Msg\nin 3\nlines'),
                    (ValueError, '2\nlines', 'ValueError: 2\nlines'),
                    ("MyStringException", None, "MyStringException"),
                    ("MyStrEx2", "My msg", "MyStrEx2: My msg")  ]:
            if isinstance(exception, basestring) and utils.py_version > (2, 5):
                continue
            try:
                raise exception, msg
            except:
                message, details = get_error_details()
                assert_equals(message, get_error_message())
            assert_equal(message, exp_msg)
            assert_true(details.startswith('Traceback'))
            assert_false(exp_msg in details)
        
    if utils.is_jython:
        
        def test_get_error_details_java(self):
            for exception, msg, expected in [
                    ('AssertionError', 'My Error', 'My Error'),
                    ('AssertionError', None, 'AssertionError'),
                    ('RuntimeException', 'Another Error', 'Another Error'),
                    ('RuntimeException', None, 'RuntimeException'),
                    ('ArithmeticException', 'foo', 'ArithmeticException: foo'), 
                    ('ArithmeticException', None, 'ArithmeticException'),
                    ('AssertionError', 'Msg\nin 3\nlines', 'Msg\nin 3\nlines'),
                    ('IOException', '1\n2', 'IOException: 1\n2'),
                    ('RuntimeException', 'java.lang.RuntimeException: embedded', 'embedded'),
                    ('IOException', 'java.io.IOException: emb', 'IOException: emb'), ]: 
                try:
                    throw_method = getattr(java_exceptions, 'throw'+exception)
                    throw_method(msg)
                except:
                    message, details = get_error_details()
                    assert_equals(message, get_error_message())
                assert_equal(message, expected)
                lines = details.splitlines()
                assert_true(exception in lines[0])
                for line in lines[1:]:
                    line.strip().startswith('at ')

        def test_message_removed_from_details_java(self):
            for msg in ['My message', 'My\nmultiline\nmessage']:
                try:
                    java_exceptions.throwRuntimeException(msg)
                except:
                    message, details = get_error_details()
                assert_true(message not in details)
                line1, line2 = details.splitlines()[0:2]
                assert_equals('java.lang.RuntimeException: ', line1)
                assert_true(line2.strip().startswith('at '))
             

if __name__ == "__main__":
    unittest.main()
