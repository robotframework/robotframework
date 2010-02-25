import unittest
from robot.utils import unic, is_jython
from robot.utils.asserts import assert_equals
if is_jython:
    from java.lang import String
    import JavaObject


class TestUnic(unittest.TestCase):

    if is_jython:
        def test_unic_with_java_object(self):
            data = u'This is unicode \xe4\xf6'
            assert_equals(unic(JavaObject(data)), data)

        def test_unic_with_class_type(self):
            assert_equals(unic(String('').getClass()), "<type 'java.lang.String'>")


if __name__ == '__main__':
    unittest.main()
