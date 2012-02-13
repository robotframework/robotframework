import os

if os.name == 'java':
    from java.lang import String
    from java.util import Hashtable, Vector
    import jarray


class _Custom:
    def __init__(self, length):
        self._length = length
    def __len__(self):
        return self._length

class _LengthMethod:
    def length(self):
        return 40
    def __str__(self):
        return 'length()'
    
class _SizeMethod:
    def size(self):
        return 41
    def __str__(self):
        return 'size()'
    
class _LengthAttribute:
    length = 42
    def __str__(self):
        return 'length'

def _create_hashtable(dictionary):
    ht = Hashtable()
    for key, value in dictionary.items():
        ht.put(key, value)
    return ht

bytes_without_non_ascii = 'hyva'
bytes_with_non_ascii = '\xe4'
tuple0 = ()
tuple1 = ('a',)
tuple2 = ('a', 'b')
tuple3 = ('a', 'b', 'c')
list0 = []
list1 = ['a']
list2 = ['a', 'b']
list3 = ['a', 'b', 'c']
dict0 = {}
dict1 = {'a':1}
dict2 = {'a':1, 'b':2}
dict3 = {'a':1, 'b':2, 'c':3}
custom0 = _Custom(0)
custom1 = _Custom(1)
custom2 = _Custom(2)
custom3 = _Custom(3)
length_method = _LengthMethod()
size_method = _SizeMethod()
length_attribute = _LengthAttribute()
if os.name == 'java':
    string0 = String()
    string1 = String('a')
    string2 = String('ab')
    string3 = String('abc')
    hashtable0 = Hashtable()
    hashtable1 = _create_hashtable(dict1)
    hashtable2 = _create_hashtable(dict2)
    hashtable3 = _create_hashtable(dict3)
    vector0 = Vector()
    vector1 = Vector(list1)
    vector2 = Vector(list2)
    vector3 = Vector(list3)
    array0 = jarray.array(list0, String)
    array1 = jarray.array(list1, String)
    array2 = jarray.array(list2, String)
    array3 = jarray.array(list3, String)
