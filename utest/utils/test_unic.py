import unittest
from robot.utils import unic, is_jython
from robot.utils.asserts import assert_equals, assert_true
if is_jython:
    from java.lang import String
    import JavaObject
    import UnicodeJavaLibrary


class TestUnic(unittest.TestCase):

    if is_jython:
        def test_with_java_object(self):
            data = u'This is unicode \xe4\xf6'
            assert_equals(unic(JavaObject(data)), data)

        def test_with_class_type(self):
            assert_true('java.lang.String' in unic(String('').getClass()))

        def test_with_array_containing_unicode_objects(self):
            assert_true('Circle is 360' in
                        unic(UnicodeJavaLibrary().javaObjectArray()))

        def test_with_iterator(self):
            iterator = UnicodeJavaLibrary().javaIterator()
            assert_true('java.util' in unic(iterator))
            assert_true('Circle is 360' in iterator.next())


if __name__ == '__main__':
    unittest.main()
