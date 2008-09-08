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
from robot import output
from robot.errors import DataError


# Note that create_list and should_(not_)_be_empty are in BuiltIn library


class _List:

    def convert_to_list(self, item):
        """Converts the given `item` to a list.
        
        Mainly useful for converting tuples to lists. Use `Create List` from
        the BuiltIn library for constructing new lists. 
        """
        return list(item)

    def append_to_list(self, list, *values):
        """Adds `values` to the end of `list`.
        
        Example:
        | Append To List | ${L1} | xxx |   |   |
        | Append To List | ${L2} | x | y | z |
        =>
        - ${L1} = ['a', 'xxx']
        - ${L2} = ['a', 'b', 'x', 'y', 'z']
        """
        for value in values:
            list.append(value)
    
    def insert_into_list(self, list, index, value):
        """Inserts `value` into `list` to the position specified with `index`.
        
        Index '0' adds the value into the first position, '1' to the second,
        and so on. Similarly, '-1' is the last position, '-2' second last, and
        so on. If the absolute value of the index is greater than the length of
        the list, the value is added at the end (positive index) or the
        beginning (negative index). An index can be given either as an integer
        or a string that can be converted to an integer. 
        
        Example:
        | Insert Into List | ${L1} | 0     | xxx |
        | Insert Into List | ${L2} | ${-1} | xxx |
        =>
        - ${L1} = ['xxx', 'a']
        - ${L2} = ['a', 'xxx', 'b']
        """
        list.insert(self._index_to_int(index), value)

    def combine_lists(self, *lists):
        """Combines the given `lists` together and returns the result.

        The given lists are never altered by this keyword.

        Example: 
        | ${x} = | Combine List | ${L1} | ${L2} |       |
        | ${y} = | Combine List | ${L1} | ${L2} | ${L1} |
        =>
        - ${x} = ['a', 'a', 'b']
        - ${y} = ['a', 'a', 'b', 'a']
        - ${L1} and ${L2} are not changed.
        """
        ret = []
        for item in lists:
            ret.extend(item)
        return ret
        
    def set_list_value(self, list, index, value):
        """Sets the value of `list` specified by `index` to the given `value`.
        
        Index '0' means the first position, '1' the second and so on.
        Similarly, '-1' is the last position, '-2' second last, and so on.
        Using an index that does not exist on the list causes an error. 
        The index can be either an integer or a string that can be converted to
        an integer.

        Example: 
        | Set List Value | ${L3} | 1 | xxx |
        =>
        - ${L3} = ['a', 'xxx', 'c']
        """ 
        try:
            list[self._index_to_int(index)] = value
        except IndexError:
            self._index_error(list, index)
    
    def remove_values_from_list(self, list, *values):
        """Removes all occurences of given `values` from `list`.
        
        Example:
        | Remove Values From List | ${L4} | a | c | e | f |
        =>
        - ${L4} = ['b', 'd']
        """
        for value in values:
            while value in list:
                list.remove(value)

    def remove_from_list(self, list, index):
        """Removes and returns the value specified with an `index` from `list`.
        
        Index '0' means the first position, '1' the second and so on.
        Similarly, '-1' is the last position, '-2' the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.
        
        Example:
        | ${x} = | Remove From List | ${L2} | 0 |
        =>
        - ${x} = 'a'
        - ${L2} = ['b']
        """
        try:
            return list.pop(self._index_to_int(index))
        except IndexError:
            self._index_error(list, index)
        
    def get_from_list(self, list, index):
        """Returns the value specified with an `index` from `list`.
        
        The given list is never altered by this keyword.
        
        Index '0' means the first position, '1' the second, and so on.
        Similarly, '-1' is the last position, '-2' the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.

        Examples (including Python equivalents in comments):
        | ${x} = | Get From List | ${L5} | 0 | # L5[0]    |
        | ${y} = | Get From List | ${L5} | 2 | # L5[2]    |
        =>
        - ${x} = 'a'
        - ${y} = 'c'
        - ${L1} and ${L2} are not changed.
        """
        try:
            return list[self._index_to_int(index)]
        except IndexError:
            self._index_error(list, index)
        
    def get_slice_from_list(self, list, start=0, end=None):
        """Returns a slice of the given list between `start` and `end` indexes.

        The given list is never altered by this keyword.
                
        If both `start` and `end` are given, a sublist containing values from
        `start` to `end` is returned. This is the same as 'list[start:end]' in
        Python. To get all items from the beginning, use 0 as the start value,
        and to get all items until the end, use 'None' as the end value. 'None'
        is also a default value, so in this case, it is enough to give only 
        `start`. If only `end` is given, `start` gets the value 0.
        
        Using `start` or `end` not found on the list is the same as using the 
        largest (or smallest) available index.
        
        Examples (incl. Python equivelants in comments):
        | ${x} = | Get Slice From List | ${L5} | 2 | 4  | # L5[2:4]    |
        | ${y} = | Get Slice From List | ${L5} | 1 |    | # L5[1:None] |
        | ${z} = | Get Slice From List | ${L5} |   | -1 | # L5[0:-2]   |
        =>
        - ${x} = ['c', 'd']
        - ${y} = ['b', 'c', 'd', 'e']
        - ${z} = ['a', 'b', 'c']
        - ${L5} is not changed.
        """
        start = self._index_to_int(start, True)
        if end is not None:
            end = self._index_to_int(end)
        return list[start:end]
        
    def count_values_in_list(self, list, value, start=0, end=None):
        """Returns the number of occurrences of the given `value` in `list`.

        The search can be narrowed to the selected sublist by the `start` and
        `end` indexes having the same semantics as in the `Get Slice From List`
        keyword. The given list is never altered by this keyword.

        | ${x} = | Count Values In List | ${L3} | b |
        =>
        - ${x} = 1
        - ${L3} is not changed.
        """
        return self.get_slice_from_list(list, start, end).count(value)
        
    def get_index_from_list(self, list, value, start=0, end=None):
        """Returns the index of the first occurrence of the `value` on the list.

        The search can be narrowed to the selected sublist by the `start` and
        `end` indexes having the same semantics as in the `Get Slice From List`
        keyword. In case the value is not found, -1 is returned. The given list
        is never altered by this keyword.

        | ${x} = | Get Index From List | ${L5} | d |
        =>
        - ${x} = 3
        - ${L5} is not changed.
        """
        if start == '':
            start = 0
        list = self.get_slice_from_list(list, start, end)
        try:
            return int(start) + list.index(value)
        except ValueError:
            return -1
        
    def copy_list(self, list):
        """Returns a copy of the given list.
        
        The given list is never altered by this keyword.
        """
        return list[:]
        
    def reverse_list(self, list):
        """Reverses the given list in place. 
        
        Note that the given list is changed and nothing is returned. Use 
        `Copy List` first, if you need to keep also the original order.

        | Reverse List | ${L3} |
        =>
        - ${L3} = ['c', 'b', 'a']        
        """
        list.reverse()
    
    def sort_list(self, list):
        """Sorts the given list in place.

        The strings are sorted alphabetically and the numbers numerically.

        Note that the given list is changed and nothing is returned. Use 
        `Copy List` first, if you need to keep also the original order.

        ${L} = [2,1,'a','c','b']
        | Sort List | ${L} |
        =>
        - ${L} = [1, 2, 'a', 'b', 'c']
        """
        list.sort()
    
    def list_should_contain_value(self, list, value, msg=None):
        """Fails if the `value` is not found from `list`.
        
        If `msg` is not given, the default error message "[ a | b | c ] does
        not contain the value 'x'" is shown in case of a failure. Otherwise,
        the given `msg` is used in case of a failure.
        """
        default = "%s does not contain value '%s'" % (utils.seq2str2(list), value)
        _verify_condition(value in list, default, msg)
    
    def list_should_not_contain_value(self, list, value, msg=None):
        """Fails if the `value` is not found from `list`.
        
        See `List Should Contain Value` for an explanation of `msg`. 
        """
        default = "%s contains value '%s'" % (utils.seq2str2(list), value)
        _verify_condition(value not in list, default, msg)
    
    def lists_should_be_equal(self, list1, list2, msg=None, values=True):
        """Fails if given lists are unequal. 
        
        The first equality of lists' length is checked, and after that all
        values. If there are differences between the values, those are listed
        in an error message, for example with lists "${L1} = [1, 2, 3]" and
        "${L2} = [0, 2, 4]".
        
        Lists are different:
        Index 0: 1 != 0
        Index 2: 3 != 4

        - If `msg` is not given, the possible error message is the default.
        - If `msg` is given and `values` is either Boolean False or a string 
          'False' or 'No Values', the error message is simply `msg`.
        - Otherwise the error message is `msg` + 'new line' + default.
        """
        len1 = len(list1); len2 = len(list2)
        default = 'Lengths are different: %d != %d' % (len1, len2)
        _verify_condition(len1 == len2, default, msg, values)
        diffs = [ 'Index %d: %s != %s' % (i, list1[i], list2[i])
                  for i in range(len1) if list1[i] != list2[i] ]
        default = 'Lists are different:\n' + '\n'.join(diffs) 
        _verify_condition(diffs == [], default, msg, values)
    
    def list_should_contain_sub_list(self, list1, list2, msg=None, values=True):
        """Fails if not all of the elements in `list2` are found in `list1`.
        
        The order of values and the number of values are not taken into account.
        
        See the use of `msg` and `values` from the `Lists Should Be Equal`
        keyword.
        """
        diffs = ', '.join([ str(item) for item in list2 if item not in list1 ])
        default = 'Following values were not found from first list: ' + diffs
        _verify_condition(diffs == '', default, msg, values)

    def log_list(self, list, level='INFO'):
        """Logs given `list's` length and content with given `level`
        
        Valid levels are TRACE, DEBUG, INFO (default), and WARN.
        
        In case you want only log the length, use keyword `Get Length` from 
        BuiltIn library. 
        """
        print '*%s* ' % (_validate_log_level(level)),
        if len(list) == 0:
            print 'List is empty'
        elif len(list) == 1:
            print "List has one item '%s'" % (list[0])
        else:
            print "List length is '%s'" % (len(list))
            for i in range(0, len(list)):
                print '%s: %s' % (i, list[i])
            
    def _index_to_int(self, index, empty_to_zero=False):    
        if empty_to_zero and index == '':
            return 0
        try:
            return int(index)
        except ValueError:
            raise ValueError("Cannot convert index '%s' to an integer" % index)

    def _index_error(self, list, index):
        raise IndexError("Given index '%s' out of range 0-%s"
                         % (index, len(list)-1))


class _Dictionary:
    
    def create_dictionary(self, *key_value_pairs):
        """Creates and returns a dictionary from the given `key_value_pairs`. 
        
        Examples:
        | ${x} = | Create Dictionary | name | value |   |   |
        | ${y} = | Create Dictionary | a    | 1     | b | 2 |
        | ${z} = | Create Dictionary | a    | ${1}  | b | ${2} |
        =>
        - ${x} = {'name': 'value'}
        - ${y} = {'a': '1', 'b': '2'}
        - ${z} = {'a': 1, 'b': 2}
        """        
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Creating a dictionary failed. There should be "
                             "an even number of key-value-pairs.")
        return self.set_to_dictionary({}, *key_value_pairs)

    def set_to_dictionary(self, dictionary, *key_value_pairs):
        """Adds the given `key_value_pairs` to the `dictionary`.
        
        Example:
        | Set To Dictionary | ${D1} | key | value | 
        =>
        - ${D1} = {'a': 1, 'key': 'value'}
        """
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Adding data to a dictionary failed. There "
                             "should be an even number of key-value-pairs.")
        for i in range(0, len(key_value_pairs), 2):
            dictionary[key_value_pairs[i]] = key_value_pairs[i+1]
        return dictionary
        
    def remove_from_dictionary(self, dictionary, *keys):
        """Removes the given `keys` from the `dictionary`.

        If the given `key` cannot be found from the `dictionary`, it is ignored.

        Example:
        | Remove From Dictionary | ${D3} | b | x | y | 
        =>
        - ${D3} = {'a': 1, 'c': 3}
        """
        for key in keys:
            try:
                value = dictionary.pop(key)
                print "Removed item with key '%s' and value '%s'" % (key, value)
            except KeyError:
                print "Key '%s' not found" % (key)

    def keep_in_dictionary(self, dictionary, *keys):
        """Keeps the given `keys` in the `dictionary` and removes all other.

        If the given `key` cannot be found from the `dictionary`, it is ignored.
        
        Example:
        | Keep In Dictionary | ${D5} | b | x | d | 
        =>
        - ${D5} = {'b': 2, 'd': 4}
        """
        remove_keys = [ key for key in dictionary.keys() if not key in keys ]
        self.remove_from_dictionary(dictionary, *remove_keys)

    def copy_dictionary(self, dictionary):
        """Returns a copy of the given dictionary.
        
        The given dictionary is never altered by this keyword.
        """
        return dictionary.copy()
    
    def get_dictionary_keys(self, dictionary):
        """Returns `keys` of the given `dictionary`.

        `Keys` are returned in sorted order. The given `dictionary` is never
        altered by this keyword.

        Example:
        | ${keys} = | Get Dictionary Keys | ${D3} |
        =>
        - ${keys} = ['a', 'b', 'c']
        """
        keys = dictionary.keys()
        keys.sort()
        return keys

    def get_dictionary_values(self, dictionary):
        """Returns values of the given dictionary.
        
        Values are returned sorted according to keys. The given dictionary is
        never altered by this keyword.

        Example:
        | ${values} = | Get Dictionary Values | ${D3} |
        =>
        - ${values} = [1, 2, 3]
        """
        return [ dictionary[k] for k in self.get_dictionary_keys(dictionary) ]
    
    def get_dictionary_items(self, dictionary):
        """Returns items of the given `dictionary`.

        Items are returned sorted by keys. The given `dictionary` is never
        altered by this keyword.

        Example:
        | ${items} = | Get Dictionary Items | ${D3} |
        =>
        - ${items} = ['a', 1, 'b', 2, 'c', 3]
        """
        ret = []
        for key in self.get_dictionary_keys(dictionary):
            ret.extend((key, dictionary[key]))
        return ret

    def get_from_dictionary(self, dictionary, key):
        """Returns a value from the given `dictionary` based on the given `key`.
        
        If the given `key` cannot be found from the `dictionary`, this keyword
        fails.
        
        The given dictionary is never altered by this keyword.

        Example:
        | ${value} = | Get From Dictionary | ${D3} | b |
        =>
        - ${value} = 2
        """
        try:
            return dictionary[key]
        except KeyError:
            raise AssertionError("Dictionary does not contain key '%s'" % key)

    def dictionary_should_contain_key(self, dictionary, key, msg=None):
        """Fails if `key` is not found from `dictionary`.
    
        See `List Should Contain Value` for an explanation of `msg`. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain key '%s'" % key
        _verify_condition(dictionary.has_key(key), default, msg)
    
    def dictionary_should_not_contain_key(self, dictionary, key, msg=None):
        """Fails if `key` is found from `dictionary`.
    
        See `List Should Contain Value` for an explanation of `msg`. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains key '%s'" % key
        _verify_condition(not dictionary.has_key(key), default, msg)

    def dictionary_should_contain_value(self, dictionary, value, msg=None):
        """Fails if `value` is not found from `dictionary`.
    
        See `List Should Contain Value` for an explanation of `msg`. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain value '%s'" % value
        _verify_condition(value in dictionary.values(), default, msg)
    
    def dictionary_should_not_contain_value(self, dictionary, value, msg=None):
        """Fails if `value` is found from `dictionary`.
    
        See `List Should Contain Value` for an explanation of `msg`. 

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains value '%s'" % value
        _verify_condition(not value in dictionary.values(), default, msg)

    def dictionaries_should_be_equal(self, dict1, dict2, msg=None, values=True):
        """Fails if the given dictionaries are not equal. 
        
        First the equality of dictionaries' keys is checked and after that all 
        the key value pairs. If there are differences between the values, those
        are listed in an error message, for example with dictionaries 
        "${D1} = {'a':1, 'b':2, 'c':3}" and "${D2} = {'a':1, 'b':4, 'c':6}".
        
        Following keys have different values:
        Key b: 2 != 4
        Key c: 3 != 6

        See `Lists Should Be Equal` for an explanation of `msg`. 
        The given dictionaries are never altered by this keyword.
        """
        keys = self._keys_should_be_equal(dict1, dict2, msg, values)
        self._key_values_should_be_equal(keys, dict1, dict2, msg, values)
        
    def dictionary_should_contain_sub_dictionary(self, dict1, dict2, msg=None, 
                                                 values=True):
        """Fails unless all items in `dict2` are found from `dict1`.

        See `Lists Should Be Equal` for an explanation of `msg`. 
        The given dictionaries are never altered by this keyword.        
        """
        keys = self.get_dictionary_keys(dict2)
        diffs = [ str(k) for k in keys if k not in dict1 ]
        default = "Following keys missing from first dictionary: %s" \
                  % ', '.join(diffs)
        _verify_condition(diffs == [], default, msg, values)
        self._key_values_should_be_equal(keys, dict1, dict2, msg, values)

    def log_dictionary(self, dictionary, level='INFO'):
        """Logs given `dictionary's` length and content with given `level`
        
        Valid levels are TRACE, DEBUG, INFO (default), and WARN.
        
        In case you want only log the length, use keyword `Get Length` from 
        BuiltIn library. 
        """
        print '*%s* ' % (_validate_log_level(level)),
        if len(dictionary) == 0:
            print 'Dictionary is empty'
        elif len(dictionary) == 1:
            print "Dictionary has one item '%s: %s'" % (dictionary.items()[0])
        else:
            print "Dictionary length is '%s'" % (len(dictionary))
            for key in self.get_dictionary_keys(dictionary):
                print '%s: %s' % (key, dictionary[key])

    def _keys_should_be_equal(self, dict1, dict2, msg, values):
        keys1 = self.get_dictionary_keys(dict1)
        keys2 = self.get_dictionary_keys(dict2)
        miss1 = [ str(k) for k in keys2 if k not in dict1 ]
        miss2 = [ str(k) for k in keys1 if k not in dict2 ]
        error = []
        if miss1:
            error += [ 'Following keys missing from first dictionary: %s'
                       % ', '.join(miss1) ]
        if miss2:
            error += [ 'Following keys missing from second dictionary: %s'
                       % ', '.join(miss2) ]
        _verify_condition(error == [], '\n'.join(error), msg, values)
        return keys1

    def _key_values_should_be_equal(self, keys, dict1, dict2, msg, values):
        diffs = [ 'Key %s: %s != %s' % (k, dict1[k], dict2[k])
                  for k in keys if dict1[k] != dict2[k] ]
        default = 'Following keys have different values:\n' + '\n'.join(diffs) 
        _verify_condition(diffs == [], default, msg, values)


class Collections(_List, _Dictionary):
    
    """A library providing keywords for handling Python lists and dictionaries.

    List keywords that do not alter given list can also be used with tuples,
    and to some extend also with other iterables.

    Following keywords from the BuiltIn library can also be used with lists and
    dictionaries:

    - `Create List`
    - `Get Length`
    - `Length Should Be`
    - `Should Be Empty`
    - `Should Not Be Empty`

    All list keywords expect a scalar variable (e.g. ${list}) as an argument.
    Possible list variables (e.g. @{list}) must thus be converted to scalar
    variables first. The example below shows how to convert between them.

    | ${list} = | Create List  | @{list} |
    | @{list} = | Set Variable | ${list} | 

    -------

    List related keywords use variables in format ${Lx} in their examples.
    this means a list with as many alphabetic characters as specified by 'x'.
    For example ${L1}' means ['a'] and ${L3} means ['a', 'b', 'c'].

    Dictionary keywords use similar ${Dx} variable. For example ${D1} means
    {'a': 1} and ${D3} means {'a': 1, 'b': 2, 'c': 3}.

    --------
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

def _validate_log_level(level):
    level = level.upper()
    if not output.LEVELS.has_key(level):
        raise DataError("Invalid log level '%s'" % level)
    return level
