import sys

if sys.platform.startswith('java'):
    from java.lang import String, Integer, Long, Float, Short, Double

    varz = { 'java_string_int': String('1'),
             'java_string_float': String('1.1'),
             'java_string_hex': String('F00'),
             'java_string_embedded_base': String('0xf00'),
             'java_string_invalid': String('foobar'),
             'java_integer': Integer(1),
             'java_long': Long(1),
             'java_short': Short(1),
             'java_float': Float(1.1),
             'java_double': Double(1.1) }

else:
    varz = {}


class MyObject:
    def __init__(self, value):
        self.value = value
    def __int__(self):
        return 42 // self.value
    def __str__(self):
        return 'MyObject'


def get_variables():
    varz['object'] = MyObject(1)
    varz['object_failing'] = MyObject(0)
    return varz
