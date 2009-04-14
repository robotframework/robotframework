# Can be used in the test data like ${MyObject()} or ${MyObject(1)}
class MyObject:
    def __init__(self, index=''):
        self.index = index
    def __str__(self):
        return '<MyObject%s>' % self.index

UNICODE = (u'Hyv\u00E4\u00E4 y\u00F6t\u00E4. '
           u'\u0421\u043F\u0430\u0441\u0438\u0431\u043E!')
LIST_WITH_OBJECTS = [MyObject(1), MyObject(2)]
NESTED_LIST = [ [True, False], [[1, None, MyObject(), {}]] ]
NESTED_TUPLE = ( (True, False), [(1, None, MyObject(), {})] )
DICT_WITH_OBJECTS = {'As value': MyObject(1), MyObject(2): 'As key'}
NESTED_DICT = { 1: {True: False},
                2: {'A': {'n': None},
                    'B': {'o': MyObject(), 'e': {}}} }
