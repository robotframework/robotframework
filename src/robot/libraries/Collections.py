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


class _List:

    #TODO: create_list exists already in BuiltIn
    
    def convert_to_list(self, item):
        """Converts given 'item' to a list.
        
        Mainly useful for converting tuples to lists. Use 'Create List' from
        BuiltIn library for constructing new lists. 
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
            print 'Appending value ' + value
            L.append(value)
    
    def insert_into_list(self, L, index, value):
        """Inserts 'value' into 'L' to position specified with 'index'.
        
        Index '0' adds the value into the first position, '1' to second and so
        on. Similarly '-1' is the last position, '-2' second last, etc. If the
        absolute value of the index is greater than the length of the list,
        value is added at the end (positive index) or beginning (negative
        index). Index can be given either as an integer or a string that can be
        converted to an integer. 
        
        Example:
        | Insert Into List | ${L1} | 0     | xxx |
        | Insert Into List | ${L2} | ${-1} | xxx |
        =>
        ${L1} == ['xxx', 'a']
        ${L2} == ['a', 'xxx', 'b']
        """
        L.insert(self._index_to_int(index), value)

    def combine_lists(self, *lists):
        """Combines given 'lists' together and returns the result

        Given lists are never altered by this keyword.

        Example: 
        | ${x} = | Combine List | ${L1} | ${L2} |       |
        | ${y} = | Combine List | ${L1} | ${L2} | ${L1} |
        =>
        ${x} == ['a', 'a', 'b']
        ${y} == ['a', 'a', 'b', 'a']
        ${L1} and ${L2} are not changed.
        """
        ret = []
        for list_ in lists:
            ret += list_
        return ret
        
    def set_list_value(self, L, index, value):
        """Sets value of 'L' specified by 'index' to given 'value'.
        
        Index '0' means the first position, '1' second and so on. Similarly '-1'
        is the last position, '-2' second last, etc. Using an index not existing
        in the list causes an error. Index can be either an integer or a string
        that can be converted to an integer.

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
        """Removes and returns value specified with index from L.
        
        Index '0' means the first position, '1' second and so on. Similarly '-1'
        is the last position, '-2' second last, etc. Using an index not existing
        in the list causes an error. Index can be either an integer or a string
        that can be converted to an integer.
        
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
        """Returns value specified with index from L.
        
        Given list is never altered by this keyword.
        
        Index '0' means the first position, '1' second and so on. Similarly '-1'
        is the last position, '-2' second last, etc. Using an index not existing
        in the list causes an error. Index can be either an integer or a string 
        that can be converted to an integer.

        Examples (incl. Python equivelants in comments):
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
        """ Return part of the given list specified with start and end indexes.

        Given list is never altered by this keyword.
                
        If both 'start' and 'end' are given then a sub list containing values
        from 'start' to 'end' is returned. This is same is 'L[start:end]' in
        Python. To get all items from the beginning use 0 as the start value
        and to get all items until to the end use None as the end value. The 
        None is also default value, so in this case it is enough to give only 
        'start'. If only 'end' is given, 'start' gets value 0.
        
        Using 'start' or 'end' not found from the list is the same as using the 
        largest (or smallest) available index.
        
        Examples (incl. Python equivelants in comments):
        | ${x} = | Get Slice From List | ${L5} | 2 | 4   | # L5[2:4]    |
        | ${y} = | Get Slice From List | ${L5} | 1 |   | # L5[1:None]  |
        | ${z} = | Get Slice From List | ${L5} |  | -1 | # L5[0:-2] |
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
        """Returns the number of occurrences of given value in L.

        Given list is never altered by this keyword.
        
        The search can be narrowed to selected sub list by 'start' and 'end'
        indexes having same semantics as in 'Get Slice From List' keyword.

        | ${x} = | Count Values In List | ${L3} | b |
        =>
        ${x} == 1
        ${L3} is not changed.
        
        """
        return self.get_slice_from_list(L, start, end).count(value)
        
    def get_index_from_list(self, L, value, start=0, end=None):
        """Returns the index of first occurrence of the value or -1 is not found.

        Given list is never altered by this keyword.
        
        The search can be narrowed to selected sub list by 'start' and 'end'
        indexes having same semantics as in 'Get Slice From List' keyword.

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
        
        Given list is never altered by this keyword.
        """
        return L[:]
        
    def reverse_list(self, L):
        """Reverses the given list in place. 
        
        Note that the given list is changed and nothing is returned. Use 
        'Copy List' first if you need to keep also the original order.

        | Reverse List | ${L3} |
        =>
        ${L3} == ['c', 'b', 'a']        
        """
        L.reverse()
    
    def sort_list(self, L):
        """Sorts the given list in place.

        Strings are sorted alphabetically and numbers numerically.

        Note that the given list is changed and nothing is returned. Use 
        'Copy List' first if you need to keep also the original order.

        ${L} = [2,1,'a','c','b']
        | Sort List | ${L} |
        =>
        ${L} == [1, 2, 'a', 'b', 'c']
        """
        L.sort()
    
    def list_should_contain_value(self, L, value, msg=None):
        """Fail if value is not found from L.
        
        If 'msg' is not given, default error message "['a', 'b', 'c'] does not 
        contain value 'x'" is shown in case of failure. Otherwise the given 
        'msg' is used in case of failure.
        """
        default = "%s does not contain value '%s'" % (utils.seq2str2(L), str(value))
        _verify_condition(L.count(value) != 0, default, msg)
    
    def list_should_not_contain_value(self, L, value, msg=None):
        """Fail if value is not found from L.
        
        See List Should Contain Value for explanation of 'msg'. 
        """
        default = "%s contains value '%s'" % (utils.seq2str2(L), str(value))
        _verify_condition(L.count(value) == 0, default, msg)
    
    def lists_should_be_equal(self, L1, L2, msg=None, values=True):
        """Fail if given lists are unequal. 
        
        First equality of lists' length is checked and after that all values.
        If there is differences between the values, those are listed in error
        message e.g. with lists ${L1} = [1, 2, 3] and ${L2} = [0, 2, 4].
        
        Lists are different:
        index, L1 value, L2 value
        0, 1, 0
        2, 3, 4

        - If 'msg' is not given the possible error message is the default.
        - If 'msg' is given and 'values' is either boolean False or string 
          'False' or 'No Values' the error message is simply 'msg'.
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
        
        The order of values and number of values are not taken into acount.
        
        See the use of 'msg' and 'values' from List Should Be Equal keyword.

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
        raise IndexError("Given index '%s' out of range 0-%s" % (index, len(L)-1))


# TODO: Should (Not) Be Empty in BuiltIn


class _Dictionary:
    
    def create_dictionary(self, *key_value_pairs):
        """Creates and returns dictionary from given 'key_value_pairs'. 
        
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
            msg = "Creating dictionary failed. There should be even number of "
            msg += "'key_value_pair' arguments."
            raise AssertionError(msg)
        return self._add_to_dictionary({}, key_value_pairs)

    def set_to_dictionary(self, dictionary, *key_value_pairs):
        """Adds given 'key_value_pairs' to dictionary.
        
        Example:
        | Set To Dictionary | ${D1} | key | value | 
        =>
        ${D1} == {'a':1, 'key':'value'}
        """
        if len(key_value_pairs) % 2 != 0:
            msg = "Adding data to dictionary failed. There should be even "
            msg += "number of 'key_value_pair' arguments."
            raise AssertionError(msg)
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
                print "Removed item with key '%s' and value '%s'" % (key, 
                                                                     str(value))
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
        
        Given dictionary is never altered by this keyword.
        """
        return dictionary.copy()
    
    def get_dictionary_keys(self, dictionary):
        """Returns keys of the given dictionary.
        
        Given dictionary is never altered by this keyword.

        Example:
        | ${keys} = | Get Dictionary Keys | ${D3} |
        =>
        ${keys} == ['a', 'b', 'c']
        """
        return dictionary.keys()

    def get_dictionary_values(self, dictionary):
        """Returns values of the given dictionary.
        
        Given dictionary is never altered by this keyword.

        Example:
        | ${values} = | Get Dictionary Values | ${D3} |
        =>
        ${values} == [1, 2, 3]
        """
        return dictionary.values()
    
    def get_dictionary_items(self, dictionary):
        """Returns items of the given dictionary.
        
        Given dictionary is never altered by this keyword.

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
        """Returns value from the given dictionary based on the given key.
        
        If the given key cannot be found from the dictionary, this keyword fails.
        
        Given dictionary is never altered by this keyword.

        Example:
        | ${value} = | Get From Dictionary | ${D3} | b |
        =>
        ${value} == 2
        """
        try:
            return dictionary[key]
        except KeyError:
            msg = "Dictionary does not contain key '%s'" % (str(key))
            raise AssertionError(msg)

    def dictionary_should_contain_key(self, dictionary, key, msg=None):
        """Fail if 'key' is not found from 'dictionary'.
    
        See List Should Contain Value for explanation of 'msg'. 

        Given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain key '%s'" % (key)
        _verify_condition(dictionary.has_key(key), default, msg)
    
    def dictionary_should_not_contain_key(self, dictionary, key, msg=None):
        """Fail if 'key' is found from 'dictionary'.
    
        See List Should Contain Value for explanation of 'msg'. 

        Given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains key '%s'" % (key)
        _verify_condition(not dictionary.has_key(key), default, msg)

    def dictionary_should_contain_value(self, dictionary, value, msg=None):
        """Fail if 'value' is not found from 'dictionary'.
    
        See List Should Contain Value for explanation of 'msg'. 

        Given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain value '%s'" % (value)
        _verify_condition(value in dictionary.values(), default, msg)
    
    def dictionary_should_not_contain_value(self, dictionary, value, msg=None):
        """Fail if 'value' is found from 'dictionary'.
    
        See List Should Contain Value for explanation of 'msg'. 

        Given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains value '%s'" % (value)
        _verify_condition(not value in dictionary.values(), default, msg)

#    def dictionary_size_should_be(self, dictionary, size, msg=None):
#        pass
    
    def dictionaries_should_be_equal(self, dict1, dict2, msg=None, values=True):
        """Fail if given lists are unequal. 
        
        First equality of dictionaries' keys is checked and after that all 
        key value pairs. If there is differences between the values, those are 
        listed in error message e.g. with dictionaries 
        ${D1} = {'a':1, 'b':2, 'c':3} and ${D2} = {'a':1, 'b':4, 'c':6}.
        
        Dictionaries are different:
        key, dict1 value, dict2 value
        b, 2, 4
        c, 3, 6

        See 'List Should Be Equal' for explanation of 'msg'. 

        Given dictionaries are never altered by this keyword.

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
        """
        Fails if not all key, value pairs in 'dict2' are found from 'dict1.'

        See 'Lists Should Be Equal' for explanation of 'msg'. 

        Given dictionaries are never altered by this keyword.        
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
    """This Library provides keywords for handling Lists and Dictionaries.

    To use list keywords with a list variable (e.g. @{list}), convert it first 
    to a scalar variable (e.g. ${list}). A scalar variable containing list can 
    also be converted to a list variable. 

    Examples:
    | ${list} = | Create List | @{list} |
    
    | @{list} = | Set Variable | ${list} | 


    In the examples ${Lx} means always a list that contains x times an alphabet
    like ${L2} = ['a', 'b']
    Similar way ${Dx} means a dictionary that contains x items with an alphabet
    key and a number value like ${D2} {'a':1, 'b':2}

    Those keywords that does not edit lists can be used with tuples.
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
