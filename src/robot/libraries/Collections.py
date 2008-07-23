#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from robot import utils


# Note that create_list and should_(not_)_be_empty are in BuiltIn library


class _List:

    def convert_to_list(self, item):
        """Converts the given 'item' to a list.
        
        Mainly useful for converting tuples to lists. Use 'Create List' from
        the BuiltIn library for constructing new lists. 
        """
        return list(item)

    def append_to_list(self, L, *values):
        """Adds 'values' to the end of L.
        
        Example:
        | Append To List | ${L1} | xxx |   |   |
        | Append To List | ${L2} | x | y | z |
        =>
        ${L1} == ['a', 'xxx']
        ${L2} == ['a', 'b', 'x', 'y', 'z']
        """
        for value in values:
            L.append(value)
    
    def insert_into_list(self, L, index, value):
        """Inserts 'value' into 'L' to the position specified with 'index'.
        
        Index '0' adds the value into the first position, '1' to the second, and
        so on. Similarly, '-1' is the last position, '-2' second last, and so
        on. If the absolute value of the index is greater than the length of the
        list, the value is added at the end (positive index) or the beginning
        (negative index). An index can be given either as an integer or a string
        that can be converted to an integer. 
        
        Example:
        | Insert Into List | ${L1} | 0     | xxx |
        | Insert Into List | ${L2} | ${-1} | xxx |
        =>
        ${L1} == ['xxx', 'a']
        ${L2} == ['a', 'xxx', 'b']
        """
        L.insert(self._index_to_int(index), value)

    def combine_lists(self, *lists):
        """Combines the given 'lists' together and returns the result.

        The given lists are never altered by this keyword.

        Example: 
        | ${x} = | Combine List | ${L1} | ${L2} |       |
        | ${y} = | Combine List | ${L1} | ${L2} | ${L1} |
        =>
        ${x} == ['a', 'a', 'b']
        ${y} == ['a', 'a', 'b', 'a']
        ${L1} and ${L2} are not changed.
        """
        ret = []
        for item in lists:
            ret.extend(item)
        return ret
        
    def set_list_value(self, L, index, value):
        """Sets the value of 'L' specified by 'index' to the given 'value'.
        
        Index '0' means the first position, '1' the second and so on. Similarly,
        '-1' is the last position, '-2' second last, and so on. Using an index
        that does not exist on the list causes an error. The index can be either
        an integer or a string that can be converted to an integer.

        Example: 
        | Set List Value | ${L3} | 1 | xxx |
        =>
        ${L3} == ['a', 'xxx', 'c']
        """ 
        try:
            L[self._index_to_int(index)] = value
        except IndexError:
            self._index_error(L, index)
    
    def remove_values_from_list(self, L, *values):
        """Removes all occurences of given value(s) from L.
        
        Example:
        | Remove Values From List | ${L4} | a | c | e | f |
        =>
        ${L4} == ['b', 'd']
        """
        for value in values:
            while value in L:
                L.remove(value)

    def remove_from_list(self, L, index):
        """Removes and returns the value specified with an index from L.
        
        Index '0' means the first position, '1' the second and so on. Similarly,
        '-1' is the last position, '-2' the second last, and so on. Using an
        index that does not exist on the list causes an error. The index can be
        either an integer or a string that can be converted to an integer.
        
        Example:
        | ${x} = | Remove From List | ${L2} | 0 |
        =>
        ${x} == 'a'
        ${L2} == ['b']
        """
        try:
            return L.pop(self._index_to_int(index))
        except IndexError:
            self._index_error(L, index)
        
    def get_from_list(self, L, index):
        """Returns the value specified with an index from L.
        
        The given list is never altered by this keyword.
        
        Index '0' means the first position, '1' the second, and so on. Similarly
        '-1' is the last position, '-2' the second last, and so on. Using an
        index that does not exist on the list causes an error. The index can be
        either an integer or a string that can be converted to an integer.

        Examples (including Python equivalents in comments):
        | ${x} = | Get From List | ${L5} | 0 | # L5[0]    |
        | ${y} = | Get From List | ${L5} | 2 | # L5[2]    |
        =>
        ${x} == 'a'
        ${y} == 'c'
        ${L1} and ${L2} are not changed.
        """
        try:
            return L[self._index_to_int(index)]
        except IndexError:
            self._index_error(L, index)
        
    def get_slice_from_list(self, L, start=0, end=None):
        """Returns a slice of the given list between start and end indexes.

        The given list is never altered by this keyword.
                
        If both 'start' and 'end' are given, a sublist containing values from
        'start' to 'end' is returned. This is the same as 'L[start:end]' in
        Python. To get all items from the beginning, use 0 as the start value,
        and to get all items until the end, use 'None' as the end value. 'None'
        is also a default value, so in this case, it is enough to give only 
        'start'. If only 'end' is given, 'start' gets the value 0.
        
        Using 'start' or 'end' not found on the list is the same as using the 
        largest (or smallest) available index.
        
        Examples (incl. Python equivelants in comments):
        | ${x} = | Get Slice From List | ${L5} | 2 | 4  | # L5[2:4]    |
        | ${y} = | Get Slice From List | ${L5} | 1 |    | # L5[1:None] |
        | ${z} = | Get Slice From List | ${L5} |   | -1 | # L5[0:-2]   |
        =>
        ${x} == ['c', 'd']
        ${y} == ['b', 'c', 'd', 'e']
        ${z} == ['a', 'b', 'c']
        ${L5} is not changed.
        """
        start = self._index_to_int(start, True)
        if end is not None:
            end = self._index_to_int(end)
        return L[start:end]
        
    def count_values_in_list(self, L, value, start=0, end=None):
        """Returns the number of occurrences of the given value in L.

        The given list is never altered by this keyword.
        
        The search can be narrowed to the selected sublist by the 'start' and
        'end' indexes having the same semantics as in the 'Get Slice From List'
        keyword.

        | ${x} = | Count Values In List | ${L3} | b |
        =>
        ${x} == 1
        ${L3} is not changed.
        
        """
        return self.get_slice_from_list(L, start, end).count(value)
        
    def get_index_from_list(self, L, value, start=0, end=None):
        """Returns the index of the first occurrence of the value on the list.

        In case the value is not found, -1 is returned.

        The given list is never altered by this keyword.
        
        The search can be narrowed to the selected sublist by the 'start' and
        'end' indexes having the same semantics as in the 'Get Slice From List'
        keyword.

        | ${x} = | Get Index From List | ${L5} | d |
        =>
        ${x} == 3
        ${L5} is not changed.
        """
        L = self.get_slice_from_list(L, start, end)
        try:
            start = start != '' and start or 0
            return int(start) + L.index(value)
        except ValueError:
            return -1
        
    def copy_list(self, L):
        """Returns a copy of the given list.
        
        The given list is never altered by this keyword.
        """
        return L[:]
        
    def reverse_list(self, L):
        """Reverses the given list in place. 
        
        Note that the given list is changed and nothing is returned. Use 
        'Copy List' first, if you need to keep also the original order.

        | Reverse List | ${L3} |
        =>
        ${L3} == ['c', 'b', 'a']        
        """
        L.reverse()
    
    def sort_list(self, L):
        """Sorts the given list in place.

        The strings are sorted alphabetically and the numbers numerically.

        Note that the given list is changed and nothing is returned. Use 
        'Copy List' first, if you need to keep also the original order.

        ${L} = [2,1,'a','c','b']
        | Sort List | ${L} |
        =>
        ${L} == [1, 2, 'a', 'b', 'c']
        """
        L.sort()
    
    def list_should_contain_value(self, L, value, msg=None):
        """Fails if the value is not found from L.
        
        If 'msg' is not given, the default error message "['a', 'b', 'c'] does
        not contain the value 'x'" is shown in case of a failure. Otherwise, the
        given 'msg' is used in case of a failure.
        """
        default = "%s does not contain value '%s'" % (utils.seq2str2(L),
                                                      str(value))
        _verify_condition(L.count(value) != 0, default, msg)
    
    def list_should_not_contain_value(self, L, value, msg=None):
        """Fails if the value is not found from L.
        
        See 'List Should Contain Value' for an explanation of 'msg'. 
        """
        default = "%s contains value '%s'" % (utils.seq2str2(L), str(value))
        _verify_condition(L.count(value) == 0, default, msg)
    
    def lists_should_be_equal(self, L1, L2, msg=None, values=True):
        """Fail if given lists are unequal. 
        
        The first equality of lists' length is checked, and after that all
        values. If there are differences between the values, those are listed in
        an error message, for example with lists "${L1} = [1, 2, 3]" and
        "${L2} = [0, 2, 4]".
        
        Lists are different:
        index, L1 value, L2 value
        0, 1, 0
        2, 3, 4

        - If 'msg' is not given, the possible error message is the default.
        - If 'msg' is given and 'values' is either Boolean False or a string 
          'False' or 'No Values', the error message is simply 'msg'.
        - Otherwise the error message is 'msg' + 'new line' + default.
        """
        default = 'Lengths are different %d!=%d' % (len(L1), len(L2))
        _verify_condition(len(L1) == len(L2), default, msg, values)


        diffs = [[i, v1, v2] for i, v1, v2 in zip(range(len(L1)), L1, L2) 
                             if v1 != v2 ] 
        default = 'Lists are different:\nindex, L1 value, L2 value'
        for d in diffs:
            default += '\n%s, %s, %s' % (str(d[0]), str(d[1]), str(d[2]))
        _verify_condition(len(diffs) == 0, default, msg, values)
    
    def list_should_contain_sub_list(self, L1, L2, msg=None, values=True):
        """Fails if not all of the elements in L2 are found in L1.
        
        The order of values and the number of values are not taken into acount.
        
        See the use of 'msg' and 'values' from the 'List Should Be Equal'
        keyword.
        """
        diffs = [value for value in L2 if not L1.count(value) > 0 ]
        default = 'Following values were not found from first list: '
        default += ', '.join(diffs)
        _verify_condition(len(diffs) == 0, default, msg, values)

    def _index_to_int(self, index, empty_to_zero=False):    
        index = empty_to_zero and index == '' and '0' or index
        try:
            return int(index)
        except ValueError:
            raise ValueError("Cannot convert index '%s' to an integer" % index)

    def _index_error(self, L, index):
        raise IndexError("Given index '%s' out of range 0-%s"
                         % (index, len(L)-1))


class _Dictionary:
    
    def create_dictionary(self, *key_value_pairs):
        """Creates and returns a dictionary from the given 'key_value_pairs'. 
        
        Examples:
        | ${x} = | Create Dictionary | name | value |   |   |
        | ${y} = | Create Dictionary | a    | 1     | b | 2 |
        | ${z} = | Create Dictionary | a    | ${1}  | b | ${2} |
        =>
        ${x} == {'name': 'value'}
        ${y} == {'a':'1', 'b':'2'}
        ${z} == {'a':1, 'b':2}
        """        
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Creating a dictionary failed. There should be "
                             "an even number of key-value-pairs.")
        return self._add_to_dictionary({}, key_value_pairs)

    def set_to_dictionary(self, dictionary, *key_value_pairs):
        """Adds the given 'key_value_pairs' to the dictionary.
        
        Example:
        | Set To Dictionary | ${D1} | key | value | 
        =>
        ${D1} == {'a':1, 'key':'value'}
        """
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Adding data to a dictionary failed. There should "
                             "be an even number of key-value-pairs.")
        self._add_to_dictionary(dictionary, key_value_pairs)

        
    def remove_from_dictionary(self, dictionary, *keys):
        """Removes the given keys from the dictionary.

        If the given key cannot be found from the dictionary, it is ignored.

        Example:
        | Remove From Dictionary | ${D3} | b | x | y | 
        =>
        ${D3} == {'a':1, 'c':3}
        """
        for key in keys:
            try:
                value = dictionary.pop(key)
                print "Removed item with key '%s' and value '%s'" % (key, value)
            except KeyError:
                print "Key '%s' not found" % (key)

    def keep_in_dictionary(self, dictionary, *keys):
        """Keeps the given keys in the dictionary and removes all other.

        If the given key cannot be found from the dictionary, it is ignored.
        
        Example:
        | Keep In Dictionary | ${D5} | b | x | d | 
        =>
        ${D5} == {'b':2, 'd':4}
        """
        remove_keys = [ key for key in dictionary.keys() if not key in keys ]
        self.remove_from_dictionary(dictionary, *remove_keys)

    def copy_dictionary(self, dictionary):
        """Returns a copy of the given dictionary.
        
        The given dictionary is never altered by this keyword.
        """
        return dictionary.copy()
    
    def get_dictionary_keys(self, dictionary):
        """Returns keys of the given dictionary.
        
        The given dictionary is never altered by this keyword.

        Example:
        | ${keys} = | Get Dictionary Keys | ${D3} |
        =>
        ${keys} == ['a', 'b', 'c']
        """
        return dictionary.keys()

    def get_dictionary_values(self, dictionary):
        """Returns values of the given dictionary.
        
        The given dictionary is never altered by this keyword.

        Example:
        | ${values} = | Get Dictionary Values | ${D3} |
        =>
        ${values} == [1, 2, 3]
        """
        return dictionary.values()
    
    def get_dictionary_items(self, dictionary):
        """Returns items of the given dictionary.
        
        The given dictionary is never altered by this keyword.

        Example:
        | ${items} = | Get Dictionary Items | ${D3} |
        =>
        ${items} == ['a', 1, 'b', 2, 'c', 3 ]
        """
        ret = []
        for item in dictionary.items():
            ret.extend(item)
        return ret

    def get_from_dictionary(self, dictionary, key):
        """Returns a value from the given dictionary based on the given key.
        
        If the given key cannot be found from the dictionary, this keyword
        fails.
        
        The given dictionary is never altered by this keyword.

        Example:
        | ${value} = | Get From Dictionary | ${D3} | b |
        =>
        ${value} == 2
        """
        try:
            return dictionary[key]
        except KeyError:
            msg = "Dictionary does not contain key '%s'" % key
            raise AssertionError(msg)

    def dictionary_should_contain_key(self, dictionary, key, msg=None):
        """Fails if 'key' is not found from 'dictionary'.
    
        See 'List Should Contain Value' for an explanation of 'msg'. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain key '%s'" % key
        _verify_condition(dictionary.has_key(key), default, msg)
    
    def dictionary_should_not_contain_key(self, dictionary, key, msg=None):
        """Fails if 'key' is found from 'dictionary'.
    
        See 'List Should Contain Value' for an explanation of 'msg'. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains key '%s'" % key
        _verify_condition(not dictionary.has_key(key), default, msg)

    def dictionary_should_contain_value(self, dictionary, value, msg=None):
        """Fails if 'value' is not found from 'dictionary'.
    
        See 'List Should Contain Value' for an explanation of 'msg'. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain value '%s'" % value
        _verify_condition(value in dictionary.values(), default, msg)
    
    def dictionary_should_not_contain_value(self, dictionary, value, msg=None):
        """Fails if 'value' is found from 'dictionary'.
    
        See 'List Should Contain Value' for an explanation of 'msg'. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains value '%s'" % value
        _verify_condition(not value in dictionary.values(), default, msg)

    def dictionaries_should_be_equal(self, dict1, dict2, msg=None, values=True):
        """Fails if the given lists are unequal. 
        
        First the equality of dictionaries' keys is checked and after that all 
        the key value pairs. If there are differences between the values, those
        are listed in an error message, for example with dictionaries 
        "${D1} = {'a':1, 'b':2, 'c':3}" and "${D2} = {'a':1, 'b':4, 'c':6}".
        
        Dictionaries are different:
        key, dict1 value, dict2 value
        b, 2, 4
        c, 3, 6

        See 'List Should Be Equal' for an explanation of 'msg'. 

        The given dictionaries are never altered by this keyword.
        """
        keys = dict1.keys()
        keys.extend(dict2.keys())
        diff_keys = [ key for key in keys 
                          if not (dict1.has_key(key) and dict2.has_key(key)) ]
        default = 'Following keys are different: %s' % (', '.join(diff_keys))
        _verify_condition(len(diff_keys) == 0, default, msg, values)
        self.dictionary_should_contain_sub_dictionary(dict1, dict2, msg, values)
        
    def dictionary_should_contain_sub_dictionary(self, dict1, dict2, msg=None, 
                                                 values=True):
        """Fails if not all key, value pairs in 'dict2' are found from 'dict1.'

        See 'Lists Should Be Equal' for an explanation of 'msg'. 

        The given dictionaries are never altered by this keyword.        
        """

        diff_keys = [ key for key in dict2.keys() if not dict1.has_key(key) ]
        default = "Following key(s) are missing from dict1: %s" 
        default = default % (', '.join(diff_keys))
        _verify_condition(len(diff_keys) == 0, default, msg, values)

        diffs = [(key, dict1[key], dict2[key]) for key in dict2.keys() 
                  if dict1[key] != dict2[key] ]
        default = 'Dictionaries are different:\nkey, dict1 value, dict2 value'
        for d in diffs:
            default += '\n%s, %s, %s' % (str(d[0]), str(d[1]), str(d[2]))
        _verify_condition(len(diffs) == 0, default, msg, values)

    def _add_to_dictionary(self, dictionary, key_value_pairs):
        for i in range(0, len(key_value_pairs), 2):
            dictionary[key_value_pairs[i]] = key_value_pairs[i+1]
        return dictionary
    

class Collections(_List, _Dictionary):
    
    """A library providing keywords for handling lists and dictionaries.

    List keywords that do not alter given list can also be used with tuples,
    and to some extend also with other iterables.

    BuiltIn library has also some related keywords. 'Create List' can obviously
    be used for creating new lists, and 'Should Be Empty' and 'Should Not Be
    Empty' work both with lists and dictionaries.

    All list keywords expect a scalar variable (e.g. ${list}) as an argument,
    and possible list variables (e.g. @{list}) must be converted to scalar
    variables first. The example below shows how to convert between them.

    | ${list} = | Create List  | @{list} |
    | @{list} = | Set Variable | ${list} | 

    ---

    List related keywords use variables in format ${Lx} in their examples.
    this means a list with as many alphabetic characters as specified by 'x'.
    For example ${L1}' means ['a'] and ${L3} means ['a', 'b', 'c'].

    Dictionary keywords use similar ${Dx} variable. For example ${D1} means
    {'a': 1} and ${D3} means {'a': 1, 'b': 2, 'c': 3}.

    ---
    """
    pass


def _verify_condition(condition, default_msg, given_msg, values=False):
    if not condition:
        values = utils.to_boolean(values, false_strs=['No Values'])
        if given_msg is None:
            raise AssertionError(default_msg)
        if values:
            raise AssertionError(given_msg + '\n' + default_msg)
        raise AssertionError(given_msg)
