#  Copyright 2008-2014 Nokia Solutions and Networks
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

from robot.api import logger
from robot.utils import plural_or_not, seq2str, seq2str2, unic, Matcher
from robot.utils.asserts import assert_equals
from robot.version import get_version


class _List:

    def convert_to_list(self, item):
        """Converts the given `item` to a list.

        Mainly useful for converting tuples and other iterable to lists.
        Use `Create List` from the BuiltIn library for constructing new lists.
        """
        return list(item)

    def append_to_list(self, list_, *values):
        """Adds `values` to the end of `list`.

        Example:
        | Append To List | ${L1} | xxx |   |   |
        | Append To List | ${L2} | x   | y | z |
        =>
        - ${L1} = ['a', 'xxx']
        - ${L2} = ['a', 'b', 'x', 'y', 'z']
        """
        for value in values:
            list_.append(value)

    def insert_into_list(self, list_, index, value):
        """Inserts `value` into `list` to the position specified with `index`.

        Index '0' adds the value into the first position, '1' to the second,
        and so on. Inserting from right works with negative indices so that
        '-1' is the second last position, '-2' third last, and so on. Use
        `Append To List` to add items to the end of the list.

        If the absolute value of the index is greater than
        the length of the list, the value is added at the end
        (positive index) or the beginning (negative index). An index
        can be given either as an integer or a string that can be
        converted to an integer.

        Example:
        | Insert Into List | ${L1} | 0     | xxx |
        | Insert Into List | ${L2} | ${-1} | xxx |
        =>
        - ${L1} = ['xxx', 'a']
        - ${L2} = ['a', 'xxx', 'b']
        """
        list_.insert(self._index_to_int(index), value)

    def combine_lists(self, *lists):
        """Combines the given `lists` together and returns the result.

        The given lists are not altered by this keyword.

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

    def set_list_value(self, list_, index, value):
        """Sets the value of `list` specified by `index` to the given `value`.

        Index '0' means the first position, '1' the second and so on.
        Similarly, '-1' is the last position, '-2' second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted to
        an integer.

        Example:
        | Set List Value | ${L3} | 1  | xxx |
        | Set List Value | ${L3} | -1 | yyy |
        =>
        - ${L3} = ['a', 'xxx', 'yyy']
        """
        try:
            list_[self._index_to_int(index)] = value
        except IndexError:
            self._index_error(list_, index)

    def remove_values_from_list(self, list_, *values):
        """Removes all occurences of given `values` from `list`.

        It is not an error is a value does not exist in the list at all.

        Example:
        | Remove Values From List | ${L4} | a | c | e | f |
        =>
        - ${L4} = ['b', 'd']
        """
        for value in values:
            while value in list_:
                list_.remove(value)

    def remove_from_list(self, list_, index):
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
            return list_.pop(self._index_to_int(index))
        except IndexError:
            self._index_error(list_, index)

    def remove_duplicates(self, list_):
        """Returns a list without duplicates based on the given `list`.

        Creates and returns a new list that contains all items in the given
        list so that one item can appear only once. Order of the items in
        the new list is the same as in the original except for missing
        duplicates. Number of the removed duplicates is logged.

        New in Robot Framework 2.7.5.
        """
        ret = []
        for item in list_:
            if item not in ret:
                ret.append(item)
        removed = len(list_) - len(ret)
        logger.info('%d duplicate%s removed.' % (removed, plural_or_not(removed)))
        return ret

    def get_from_list(self, list_, index):
        """Returns the value specified with an `index` from `list`.

        The given list is never altered by this keyword.

        Index '0' means the first position, '1' the second, and so on.
        Similarly, '-1' is the last position, '-2' the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.

        Examples (including Python equivalents in comments):
        | ${x} = | Get From List | ${L5} | 0  | # L5[0]  |
        | ${y} = | Get From List | ${L5} | -2 | # L5[-2] |
        =>
        - ${x} = 'a'
        - ${y} = 'd'
        - ${L5} is not changed
        """
        try:
            return list_[self._index_to_int(index)]
        except IndexError:
            self._index_error(list_, index)

    def get_slice_from_list(self, list_, start=0, end=None):
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
        | ${z} = | Get Slice From List | ${L5} |   | -2 | # L5[0:-2]   |
        =>
        - ${x} = ['c', 'd']
        - ${y} = ['b', 'c', 'd', 'e']
        - ${z} = ['a', 'b', 'c']
        - ${L5} is not changed
        """
        start = self._index_to_int(start, True)
        if end is not None:
            end = self._index_to_int(end)
        return list_[start:end]

    def count_values_in_list(self, list_, value, start=0, end=None):
        """Returns the number of occurrences of the given `value` in `list`.

        The search can be narrowed to the selected sublist by the `start` and
        `end` indexes having the same semantics as in the `Get Slice From List`
        keyword. The given list is never altered by this keyword.

        Example:
        | ${x} = | Count Values In List | ${L3} | b |
        =>
        - ${x} = 1
        - ${L3} is not changed
        """
        return self.get_slice_from_list(list_, start, end).count(value)

    def get_index_from_list(self, list_, value, start=0, end=None):
        """Returns the index of the first occurrence of the `value` on the list.

        The search can be narrowed to the selected sublist by the `start` and
        `end` indexes having the same semantics as in the `Get Slice From List`
        keyword. In case the value is not found, -1 is returned. The given list
        is never altered by this keyword.

        Example:
        | ${x} = | Get Index From List | ${L5} | d |
        =>
        - ${x} = 3
        - ${L5} is not changed
        """
        if start == '':
            start = 0
        list_ = self.get_slice_from_list(list_, start, end)
        try:
            return int(start) + list_.index(value)
        except ValueError:
            return -1

    def copy_list(self, list_):
        """Returns a copy of the given list.

        The given list is never altered by this keyword.
        """
        return list_[:]

    def reverse_list(self, list_):
        """Reverses the given list in place.

        Note that the given list is changed and nothing is returned. Use
        `Copy List` first, if you need to keep also the original order.

        | Reverse List | ${L3} |
        =>
        - ${L3} = ['c', 'b', 'a']
        """
        list_.reverse()

    def sort_list(self, list_):
        """Sorts the given list in place.

        The strings are sorted alphabetically and the numbers numerically.

        Note that the given list is changed and nothing is returned. Use
        `Copy List` first, if you need to keep also the original order.

        ${L} = [2,1,'a','c','b']
        | Sort List | ${L} |
        =>
        - ${L} = [1, 2, 'a', 'b', 'c']
        """
        list_.sort()

    def list_should_contain_value(self, list_, value, msg=None):
        """Fails if the `value` is not found from `list`.

        If `msg` is not given, the default error message "[ a | b | c ] does
        not contain the value 'x'" is shown in case of a failure. Otherwise,
        the given `msg` is used in case of a failure.
        """
        default = "%s does not contain value '%s'." % (seq2str2(list_), value)
        _verify_condition(value in list_, default, msg)

    def list_should_not_contain_value(self, list_, value, msg=None):
        """Fails if the `value` is not found from `list`.

        See `List Should Contain Value` for an explanation of `msg`.
        """
        default = "%s contains value '%s'." % (seq2str2(list_), value)
        _verify_condition(value not in list_, default, msg)

    def list_should_not_contain_duplicates(self, list_, msg=None):
        """Fails if any element in the `list` is found from it more than once.

        The default error message lists all the elements that were found
        from the `list` multiple times, but it can be overridden by giving
        a custom `msg`. All multiple times found items and their counts are
        also logged.

        This keyword works with all iterables that can be converted to a list.
        The original iterable is never altered.
        """
        if not isinstance(list_, list):
            list_ = list(list_)
        dupes = []
        for item in list_:
            if item not in dupes:
                count = list_.count(item)
                if count > 1:
                    logger.info("'%s' found %d times." % (item, count))
                    dupes.append(item)
        if dupes:
            raise AssertionError(msg or
                                 '%s found multiple times.' % seq2str(dupes))

    def lists_should_be_equal(self, list1, list2, msg=None, values=True,
                              names=None):
        """Fails if given lists are unequal.

        The keyword first verifies that the lists have equal lengths, and then
        it checks are all their values equal. Possible differences between the
        values are listed in the default error message like `Index 4: ABC !=
        Abc`.

        The error message can be configured using `msg` and `values` arguments:
        - If `msg` is not given, the default error message is used.
        - If `msg` is given and `values` is either Boolean False or a string
          'False' or 'No Values', the error message is simply `msg`.
        - Otherwise the error message is `msg` + 'new line' + default.

        Optional `names` argument (new in 2.6) can be used for naming
        the indices shown in the default error message. It can either
        be a list of names matching the indices in the lists or a
        dictionary where keys are indices that need to be named. It is
        not necessary to name all of the indices.  When using a
        dictionary, keys can be either integers or strings that can be
        converted to integers.

        Examples:
        | ${names} = | Create List | First Name | Family Name | Email |
        | Lists Should Be Equal | ${people1} | ${people2} | names=${names} |
        | ${names} = | Create Dictionary | 0 | First Name | 2 | Email |
        | Lists Should Be Equal | ${people1} | ${people2} | names=${names} |

        If the items in index 2 would differ in the above examples, the error
        message would contain a row like `Index 2 (email): name@foo.com !=
        name@bar.com`.
        """
        len1 = len(list1)
        len2 = len(list2)
        default = 'Lengths are different: %d != %d' % (len1, len2)
        _verify_condition(len1 == len2, default, msg, values)
        names = self._get_list_index_name_mapping(names, len1)
        diffs = list(self._yield_list_diffs(list1, list2, names))
        default = 'Lists are different:\n' + '\n'.join(diffs)
        _verify_condition(diffs == [], default, msg, values)

    def _get_list_index_name_mapping(self, names, list_length):
        if not names:
            return {}
        if isinstance(names, dict):
            return dict((int(index), names[index]) for index in names)
        return dict(zip(range(list_length), names))

    def _yield_list_diffs(self, list1, list2, names):
        for index, (item1, item2) in enumerate(zip(list1, list2)):
            name = ' (%s)' % names[index] if index in names else ''
            try:
                assert_equals(item1, item2, msg='Index %d%s' % (index, name))
            except AssertionError, err:
                yield unic(err)

    def list_should_contain_sub_list(self, list1, list2, msg=None, values=True):
        """Fails if not all of the elements in `list2` are found in `list1`.

        The order of values and the number of values are not taken into
        account.

        See the use of `msg` and `values` from the `Lists Should Be Equal`
        keyword.
        """
        diffs = ', '.join(unic(item) for item in list2 if item not in list1)
        default = 'Following values were not found from first list: ' + diffs
        _verify_condition(not diffs, default, msg, values)

    def log_list(self, list_, level='INFO'):
        """Logs the length and contents of the `list` using given `level`.

        Valid levels are TRACE, DEBUG, INFO (default), and WARN.

        If you only want to the length, use keyword `Get Length` from
        the BuiltIn library.
        """
        logger.write('\n'.join(self._log_list(list_)), level)

    def _log_list(self, list_):
        if not list_:
            yield 'List is empty.'
        elif len(list_) == 1:
            yield 'List has one item:\n%s' % list_[0]
        else:
            yield 'List length is %d and it contains following items:' % len(list_)
            for index, item in enumerate(list_):
                yield '%s: %s' % (index, item)

    def _index_to_int(self, index, empty_to_zero=False):
        if empty_to_zero and not index:
            return 0
        try:
            return int(index)
        except ValueError:
            raise ValueError("Cannot convert index '%s' to an integer." % index)

    def _index_error(self, list_, index):
        raise IndexError('Given index %s is out of the range 0-%d.'
                         % (index, len(list_)-1))


class _Dictionary:

    def create_dictionary(self, *key_value_pairs, **items):
        """Creates and returns a dictionary based on given items.

        Giving items as `key_value_pairs` means giving keys and values
        as separate arguments:

        | ${x} = | Create Dictionary | name | value |   |      |
        | ${y} = | Create Dictionary | a    | 1     | b | ${2} |
        =>
        - ${x} = {'name': 'value'}
        - ${y} = {'a': '1', 'b': 2}

        Starting from Robot Framework 2.8.1, items can also be given as kwargs:

        | ${x} = | Create Dictionary | name=value |        |
        | ${y} = | Create Dictionary | a=1        | b=${2} |

        The latter syntax is typically more convenient to use, but it has
        a limitation that keys must be strings.
        """
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Creating a dictionary failed. There should be "
                             "even number of key-value-pairs.")
        return self.set_to_dictionary({}, *key_value_pairs, **items)

    def set_to_dictionary(self, dictionary, *key_value_pairs, **items):
        """Adds the given `key_value_pairs` and `items` to the `dictionary`.

        See `Create Dictionary` for information about giving items.
        If the given `key` already exist in the `dictionary`, its value
        is updated.

        Example:
        | Set To Dictionary | ${D1} | key | value |
        =>
        - ${D1} = {'a': 1, 'key': 'value'}
        """
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Adding data to a dictionary failed. There "
                             "should be even number of key-value-pairs.")
        for i in range(0, len(key_value_pairs), 2):
            dictionary[key_value_pairs[i]] = key_value_pairs[i+1]
        dictionary.update(items)
        return dictionary

    def remove_from_dictionary(self, dictionary, *keys):
        """Removes the given `keys` from the `dictionary`.

        If the given `key` cannot be found from the `dictionary`, it
        is ignored.

        Example:
        | Remove From Dictionary | ${D3} | b | x | y |
        =>
        - ${D3} = {'a': 1, 'c': 3}
        """
        for key in keys:
            if key in dictionary:
                value = dictionary.pop(key)
                logger.info("Removed item with key '%s' and value '%s'." % (key, value))
            else:
                logger.info("Key '%s' not found." % key)

    def keep_in_dictionary(self, dictionary, *keys):
        """Keeps the given `keys` in the `dictionary` and removes all other.

        If the given `key` cannot be found from the `dictionary`, it
        is ignored.

        Example:
        | Keep In Dictionary | ${D5} | b | x | d |
        =>
        - ${D5} = {'b': 2, 'd': 4}
        """
        remove_keys = [k for k in dictionary if k not in keys]
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
        return sorted(dictionary)

    def get_dictionary_values(self, dictionary):
        """Returns values of the given dictionary.

        Values are returned sorted according to keys. The given dictionary is
        never altered by this keyword.

        Example:
        | ${values} = | Get Dictionary Values | ${D3} |
        =>
        - ${values} = [1, 2, 3]
        """
        return [dictionary[k] for k in self.get_dictionary_keys(dictionary)]

    def get_dictionary_items(self, dictionary):
        """Returns items of the given `dictionary`.

        Items are returned sorted by keys. The given `dictionary` is not
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
            raise RuntimeError("Dictionary does not contain key '%s'." % key)

    def dictionary_should_contain_key(self, dictionary, key, msg=None):
        """Fails if `key` is not found from `dictionary`.

        See `List Should Contain Value` for an explanation of `msg`.

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain key '%s'." % key
        _verify_condition(key in dictionary, default, msg)

    def dictionary_should_not_contain_key(self, dictionary, key, msg=None):
        """Fails if `key` is found from `dictionary`.

        See `List Should Contain Value` for an explanation of `msg`.

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains key '%s'." % key
        _verify_condition(key not in dictionary, default, msg)

    def dictionary_should_contain_item(self, dictionary, key, value, msg=None):
        """An item of `key`/`value` must be found in a `dictionary`.

        Value is converted to unicode for comparison.

        See `Lists Should Be Equal` for an explanation of `msg`.
        The given dictionary is never altered by this keyword.
        """
        self.dictionary_should_contain_key(dictionary, key, msg)
        actual, expected = unicode(dictionary[key]), unicode(value)
        default = "Value of dictionary key '%s' does not match: %s != %s" % (key, actual, expected)
        _verify_condition(actual == expected, default, msg)

    def dictionary_should_contain_value(self, dictionary, value, msg=None):
        """Fails if `value` is not found from `dictionary`.

        See `List Should Contain Value` for an explanation of `msg`.

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary does not contain value '%s'." % value
        _verify_condition(value in dictionary.values(), default, msg)

    def dictionary_should_not_contain_value(self, dictionary, value, msg=None):
        """Fails if `value` is found from `dictionary`.

        See `List Should Contain Value` for an explanation of `msg`.

        The given dictionary is never altered by this keyword.
        """
        default = "Dictionary contains value '%s'." % value
        _verify_condition(not value in dictionary.values(), default, msg)

    def dictionaries_should_be_equal(self, dict1, dict2, msg=None, values=True):
        """Fails if the given dictionaries are not equal.

        First the equality of dictionaries' keys is checked and after that all
        the key value pairs. If there are differences between the values, those
        are listed in the error message.

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
        diffs = [unic(k) for k in keys if k not in dict1]
        default = "Following keys missing from first dictionary: %s" \
                  % ', '.join(diffs)
        _verify_condition(not diffs, default, msg, values)
        self._key_values_should_be_equal(keys, dict1, dict2, msg, values)

    def log_dictionary(self, dictionary, level='INFO'):
        """Logs the size and contents of the `dictionary` using given `level`.

        Valid levels are TRACE, DEBUG, INFO (default), and WARN.

        If you only want to log the size, use keyword `Get Length` from
        the BuiltIn library.
        """
        logger.write('\n'.join(self._log_dictionary(dictionary)), level)

    def _log_dictionary(self, dictionary):
        if not dictionary:
            yield 'Dictionary is empty.'
        elif len(dictionary) == 1:
            yield 'Dictionary has one item:'
        else:
            yield 'Dictionary size is %d and it contains following items:' % len(dictionary)
        for key in self.get_dictionary_keys(dictionary):
            yield '%s: %s' % (key, dictionary[key])

    def _keys_should_be_equal(self, dict1, dict2, msg, values):
        keys1 = self.get_dictionary_keys(dict1)
        keys2 = self.get_dictionary_keys(dict2)
        miss1 = [unic(k) for k in keys2 if k not in dict1]
        miss2 = [unic(k) for k in keys1 if k not in dict2]
        error = []
        if miss1:
            error += ['Following keys missing from first dictionary: %s'
                      % ', '.join(miss1)]
        if miss2:
            error += ['Following keys missing from second dictionary: %s'
                      % ', '.join(miss2)]
        _verify_condition(not error, '\n'.join(error), msg, values)
        return keys1

    def _key_values_should_be_equal(self, keys, dict1, dict2, msg, values):
        diffs = list(self._yield_dict_diffs(keys, dict1, dict2))
        default = 'Following keys have different values:\n' + '\n'.join(diffs)
        _verify_condition(not diffs, default, msg, values)

    def _yield_dict_diffs(self, keys, dict1, dict2):
        for key in keys:
            try:
                assert_equals(dict1[key], dict2[key], msg='Key %s' % (key,))
            except AssertionError, err:
                yield unic(err)


class Collections(_List, _Dictionary):

    """A test library providing keywords for handling lists and dictionaries.

    `Collections` is Robot Framework's standard library that provides a
    set of keywords for handling Python lists and dictionaries. This
    library has keywords, for example, for modifying and getting
    values from lists and dictionaries (e.g. `Append To List`, `Get
    From Dictionary`) and for verifying their contents (e.g. `Lists
    Should Be Equal`, `Dictionary Should Contain Value`).

    Following keywords from the BuiltIn library can also be used with
    lists and dictionaries:
    | *Keyword Name*               | *Applicable With* |
    | `Create List`                | lists |
    | `Get Length`                 | both  |
    | `Length Should Be`           | both  |
    | `Should Be Empty`            | both  |
    | `Should Not Be Empty`        | both  |
    | `Should Contain`             | lists |
    | `Should Not Contain`         | lists |
    | `Should Contain X Times`     | lists |
    | `Should Not Contain X Times` | lists |
    | `Get Count`                  | lists |

    All list keywords expect a scalar variable (e.g. ${list}) as an
    argument.  It is, however, possible to use list variables
    (e.g. @{list}) as scalars simply by replacing '@' with '$'.

    List keywords that do not alter the given list can also be used
    with tuples, and to some extend also with other iterables.
    `Convert To List` can be used to convert tuples and other iterables
    to lists.

    -------

    List related keywords use variables in format ${Lx} in their examples,
    which means a list with as many alphabetic characters as specified by 'x'.
    For example ${L1} means ['a'] and ${L3} means ['a', 'b', 'c'].

    Dictionary keywords use similar ${Dx} variables. For example ${D1} means
    {'a': 1} and ${D3} means {'a': 1, 'b': 2, 'c': 3}.

    --------
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def should_contain_match(self, list, pattern, msg=None,
                             case_insensitive=False,
                             whitespace_insensitive=False):
        """Fails if `pattern` is not found in `list`.

        See `List Should Contain Value` for an explanation of `msg`.

        By default, pattern matching is similar to matching files in a shell
        and is case-sensitive and whitespace-sensitive. In the pattern syntax,
        '*' matches to anything and '?' matches to any single character. You
        can also prepend 'glob=' to your pattern to explicitly use this pattern
        matching behavior.

        If you prepend 'regexp=' to your pattern, your pattern will be used
        according to the Python
        [http://docs.python.org/2/library/re.html|re module] regular expression
        syntax. Important note: Backslashes are an escape character, and must
        be escaped with another backslash (e.g. 'regexp=\\\\d{6}' to search for
        '\\d{6}'). See `BuiltIn.Should Match Regexp` for more details.

        If `case_insensitive` is True, the pattern matching will ignore case.

        If `whitespace_insensitive` is True, the pattern matching will ignore
        whitespace.

        Non-string values in lists are ignored when matching patterns.

        The given list is never altered by this keyword.

        See also `Should Not Contain Match`.

        Examples:
        | Should Contain Match | ${list} | a* | # List should contain any string beginning with 'a' |
        | Should Contain Match | ${list} | regexp=a.* | # List should contain any string beginning with 'a' (regexp version) |
        | Should Contain Match | ${list} | regexp=\\\\d{6} | # List should contain any string which contains six decimal digits |
        | Should Contain Match | ${list} | a* | case_insensitive=${True} | # List should contain any string beginning with 'a' or 'A' |
        | Should Contain Match | ${list} | ab* | whitespace_insensitive=${True} | # List should contain any string beginning with 'ab' or 'a b' or any other combination of whitespace |
        | Should Contain Match | ${list} | ab* | whitespace_insensitive=${True} | case_insensitive=${True} | # List should contain any string beginning with 'ab' or 'a b' or 'AB' or 'A B' or any other combination of whitespace and upper/lower case 'a' and 'b' |

        New in Robot Framework 2.8.6.
        """
        default = "%s does not contain match for pattern '%s'." % (
            seq2str2(list), pattern)
        _verify_condition(
            _get_matches_in_iterable(list, pattern, case_insensitive,
                                     whitespace_insensitive), default, msg)

    def should_not_contain_match(self, list, pattern, msg=None,
                                 case_insensitive=False,
                                 whitespace_insensitive=False):
        """Fails if `pattern` is found in `list`.

        See `List Should Contain Value` for an explanation of `msg`.

        See `Should Contain Match` for usage details and examples.

        New in Robot Framework 2.8.6.
        """
        default = "%s contains match for pattern '%s'." % (
            seq2str2(list), pattern)
        _verify_condition(
            not _get_matches_in_iterable(list, pattern, case_insensitive,
                                         whitespace_insensitive), default, msg)

    def get_matches(self, list, pattern, case_insensitive=False,
                    whitespace_insensitive=False):
        """Returns a list of matches to `pattern` in `list`.

        For more information on `pattern`, `case_insensitive`, and
        `whitespace_insensitive`, see `Should Contain Match`.

        Examples:
        | ${matches}= | Get Matches | ${list} | a* | # ${matches} will contain any string beginning with 'a' |
        | ${matches}= | Get Matches | ${list} | regexp=a.* | # ${matches} will contain any string beginning with 'a' (regexp version) |
        | ${matches}= | Get Matches | ${list} | a* | case_insensitive=${True} | # ${matches} will contain any string beginning with 'a' or 'A' |

        New in Robot Framework 2.8.6.
        """
        return _get_matches_in_iterable(list, pattern, case_insensitive,
                                        whitespace_insensitive)

    def get_match_count(self, list, pattern, case_insensitive=False,
                        whitespace_insensitive=False):
        """Returns the count of matches to `pattern` in `list`.

        For more information on `pattern`, `case_insensitive`, and
        `whitespace_insensitive`, see `Should Contain Match`.

        Examples:
        | ${count}= | Get Match Count | ${list} | a* | # ${count} will be the count of strings beginning with 'a' |
        | ${count}= | Get Match Count | ${list} | regexp=a.* | # ${matches} will be the count of strings beginning with 'a' (regexp version) |
        | ${count}= | Get Match Count | ${list} | a* | case_insensitive=${True} | # ${matches} will be the count of strings beginning with 'a' or 'A' |

        New in Robot Framework 2.8.6.
        """
        return len(self.get_matches(list, pattern, case_insensitive,
                                    whitespace_insensitive))


def _verify_condition(condition, default_msg, given_msg, include_default=False):
    if not condition:
        if not given_msg:
            raise AssertionError(default_msg)
        if _include_default_message(include_default):
            raise AssertionError(given_msg + '\n' + default_msg)
        raise AssertionError(given_msg)

def _include_default_message(include):
    if isinstance(include, basestring):
        return include.lower() not in ['no values', 'false']
    return bool(include)


def _get_matches_in_iterable(iterable, pattern, case_insensitive=False,
                             whitespace_insensitive=False):
    if not iterable:
        return []
    regexp = False
    if not isinstance(pattern, basestring):
        raise TypeError(
            "Pattern must be string, got '%s'." % type(pattern).__name__)
    if pattern.startswith('regexp='):
        pattern = pattern[7:]
        regexp = True
    elif pattern.startswith('glob='):
        pattern = pattern[5:]
    matcher = Matcher(pattern, caseless=case_insensitive,
                      spaceless=whitespace_insensitive, regexp=regexp)
    return [string for string in iterable
            if isinstance(string, basestring)
            and matcher.match(string)]
