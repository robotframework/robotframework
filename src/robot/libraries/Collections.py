#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import copy
from collections.abc import (
    Iterator, Mapping, MutableMapping, MutableSequence, Sequence, Set
)
from itertools import chain
from typing import Literal, NoReturn, Union

from robot.api import logger
from robot.utils import (
    Matcher, NotSet, plural_or_not as s, seq2str, seq2str2, type_name
)
from robot.utils.asserts import assert_equal
from robot.version import get_version

from .normalizer import IgnoreCase, Normalizer

NOT_SET = NotSet()

ListLike = Union[Sequence, Mapping, Set]


class _List:

    def convert_to_list(self, item: object) -> list:
        """Converts the given ``item`` to a Python ``list`` type.

        Mainly useful for converting tuples and other iterable to lists.
        Use `Create List` from the BuiltIn library for constructing new lists.

        To split strings into characters, the `Split String To Characters` from
        the String Library can be used.
        """
        return list(item)  # type: ignore

    def append_to_list(
        self,
        list_: MutableSequence,
        *values: object,
    ) -> MutableSequence:
        """Adds ``values`` to the end of ``list``.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Example:
        | Append To List | ${L1} | xxx |   |   |
        | Append To List | ${L2} | x   | y | z |
        =>
        | ${L1} = ['a', 'xxx']
        | ${L2} = ['a', 'b', 'x', 'y', 'z']
        """
        list_.extend(values)
        return list_

    def insert_into_list(
        self,
        list_: MutableSequence,
        index: int,
        value: object,
    ) -> MutableSequence:
        """Inserts ``value`` into ``list`` to the position specified with ``index``.

        Index ``0`` adds the value into the first position, ``1`` to the second,
        and so on. Inserting from right works with negative indices so that
        ``-1`` is the second last position, ``-2`` third last, and so on. Use
        `Append To List` to add items to the end of the list.

        If the absolute value of the index is greater than
        the length of the list, the value is added at the end
        (positive index) or the beginning (negative index). An index
        can be given either as an integer or a string that can be
        converted to an integer.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Example:
        | Insert Into List | ${L1} | 0     | xxx |
        | Insert Into List | ${L2} | ${-1} | xxx |
        =>
        | ${L1} = ['xxx', 'a']
        | ${L2} = ['a', 'xxx', 'b']
        """
        list_.insert(index, value)
        return list_

    def combine_lists(self, *lists: ListLike) -> list:
        """Combines the given ``lists`` together and returns the result.

        The given lists are not altered by this keyword.

        Example:
        | ${x} = | Combine Lists | ${L1} | ${L2} |       |
        | ${y} = | Combine Lists | ${L1} | ${L2} | ${L1} |
        =>
        | ${x} = ['a', 'a', 'b']
        | ${y} = ['a', 'a', 'b', 'a']
        | ${L1} and ${L2} are not changed.
        """
        return list(chain.from_iterable(lists))

    def set_list_value(
        self,
        list_: MutableSequence,
        index: int,
        value: object,
    ) -> MutableSequence:
        """Sets the value of ``list`` specified by ``index`` to the given ``value``.

        Index ``0`` means the first position, ``1`` the second and so on.
        Similarly, ``-1`` is the last position, ``-2`` second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted to
        an integer.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Example:
        | Set List Value | ${L3} | 1  | xxx |
        | Set List Value | ${L3} | -1 | yyy |
        =>
        | ${L3} = ['a', 'xxx', 'yyy']

        Starting from Robot Framework 6.1, it is also possible to use the native
        item assignment syntax. This is equivalent to the above:
        | ${L3}[1] =  | Set Variable | xxx |
        | ${L3}[-1] = | Set Variable | yyy |
        """
        try:
            list_[index] = value
        except IndexError:
            self._index_error(list_, index)
        return list_

    def remove_values_from_list(
        self,
        list_: MutableSequence,
        *values: object,
    ) -> MutableSequence:
        """Removes all occurrences of given ``values`` from ``list``.

        It is not an error if a value does not exist in the list at all.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Example:
        | Remove Values From List | ${L4} | a | c | e | f |
        =>
        | ${L4} = ['b', 'd']
        """
        for value in values:
            while value in list_:
                list_.remove(value)
        return list_

    def remove_from_list(self, list_: MutableSequence, index: int) -> object:
        """Removes and returns the value specified with an ``index`` from ``list``.

        Index ``0`` means the first position, ``1`` the second and so on.
        Similarly, ``-1`` is the last position, ``-2`` the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.

        Example:
        | ${x} = | Remove From List | ${L2} | 0 |
        =>
        | ${x} = 'a'
        | ${L2} = ['b']
        """
        try:
            return list_.pop(index)
        except IndexError:
            self._index_error(list_, index)

    def remove_duplicates(self, list_: Sequence) -> list:
        """Returns a list without duplicates based on the given ``list``.

        Creates and returns a new list that contains all items in the given
        list so that one item can appear only once. Order of the items in
        the new list is the same as in the original except for missing
        duplicates. Number of the removed duplicates is logged.
        """
        ret = []
        for item in list_:
            if item not in ret:
                ret.append(item)
        removed = len(list_) - len(ret)
        logger.info(f"{removed} duplicate{s(removed)} removed.")
        return ret

    def get_from_list(self, list_: Sequence, index: int) -> object:
        """Returns the value specified with an ``index`` from ``list``.

        The given list is never altered by this keyword.

        Index ``0`` means the first position, ``1`` the second, and so on.
        Similarly, ``-1`` is the last position, ``-2`` the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.

        Examples (including Python equivalents in comments):
        | ${x} = | Get From List | ${L5} | 0  | # L5[0]  |
        | ${y} = | Get From List | ${L5} | -2 | # L5[-2] |
        =>
        | ${x} = 'a'
        | ${y} = 'd'
        | ${L5} is not changed
        """
        try:
            return list_[index]
        except IndexError:
            self._index_error(list_, index)

    def get_slice_from_list(
        self,
        list_: Sequence,
        start: "int | Literal['']" = 0,
        end: "int | None" = None,
    ) -> Sequence:
        """Returns a slice of the given list between ``start`` and ``end`` indexes.

        The given list is never altered by this keyword.

        If both ``start`` and ``end`` are given, a sublist containing values
        from ``start`` to ``end`` is returned. This is the same as
        ``list[start:end]`` in Python. To get all items from the beginning,
        use 0 as the start value, and to get all items until and including
        the end, use ``None`` (default) as the end value.

        Using ``start`` or ``end`` not found on the list is the same as using
        the largest (or smallest) available index.

        Examples (incl. Python equivalents in comments):
        | ${x} = | Get Slice From List | ${L5} | 2      | 4 | # L5[2:4]    |
        | ${y} = | Get Slice From List | ${L5} | 1      |   | # L5[1:None] |
        | ${z} = | Get Slice From List | ${L5} | end=-2 |   | # L5[0:-2]   |
        =>
        | ${x} = ['c', 'd']
        | ${y} = ['b', 'c', 'd', 'e']
        | ${z} = ['a', 'b', 'c']
        | ${L5} is not changed
        """
        if start == "":
            # Deprecated in RF 7.4. TODO: Remove in RF 9.
            logger.warn(
                "Using an empty string as a start index with the 'Get Slice From List' "
                "keyword is deprecated. Use '0' instead."
            )
            start = 0
        return list_[start:end]

    def count_values_in_list(
        self,
        list_: Sequence,
        value: object,
        start: int = 0,
        end: "int | None" = None,
    ) -> int:
        """Returns the number of occurrences of the given ``value`` in ``list``.

        The search can be narrowed to the selected sublist by the ``start`` and
        ``end`` indexes having the same semantics as with `Get Slice From List`
        keyword. The given list is never altered by this keyword.

        Example:
        | ${x} = | Count Values In List | ${L3} | b |
        =>
        | ${x} = 1
        | ${L3} is not changed
        """
        return self.get_slice_from_list(list_, start, end).count(value)

    def get_index_from_list(
        self,
        list_: Sequence,
        value: object,
        start: "int | Literal['']" = 0,
        end: "int | None" = None,
    ) -> int:
        """Returns the index of the first occurrence of the ``value`` on the list.

        The search can be narrowed to the selected sublist by the ``start`` and
        ``end`` indexes having the same semantics as with `Get Slice From List`
        keyword. In case the value is not found, -1 is returned. The given list
        is never altered by this keyword.

        Example:
        | ${x} = | Get Index From List | ${L5} | d |
        =>
        | ${x} = 3
        | ${L5} is not changed
        """
        if start == "":
            # Deprecated in RF 7.4. TODO: Remove in RF 9.
            logger.warn(
                "Using an empty string as a start index with the 'Get Index From List' "
                "keyword is deprecated. Use '0' instead."
            )
            start = 0
        list_ = self.get_slice_from_list(list_, start, end)
        try:
            return start + list_.index(value)
        except ValueError:
            return -1

    def copy_list(self, list_: Sequence, deepcopy: bool = False) -> Sequence:
        """Returns a copy of the given list.

        By default, returns a new list with same items as in the original.
        Set the ``deepcopy`` argument to a true value if also items should
        be copied.

        The given list is never altered by this keyword.
        """
        if deepcopy:
            return copy.deepcopy(list_)
        return list_[:]

    def reverse_list(self, list_: MutableSequence) -> MutableSequence:
        """Reverses the given list in place.

        Note that the given list is changed and nothing is returned. Use
        `Copy List` first, if you need to keep also the original order.

        Starting from Robot Framework 7.4, the reversed list is also returned.

        | Reverse List | ${L3} |
        =>
        | ${L3} = ['c', 'b', 'a']
        """
        list_.reverse()
        return list_

    def sort_list(self, list_: MutableSequence) -> MutableSequence:
        """Sorts the given list in place.

        Sorting fails if items in the list are not comparable with each others.
        For example, sorting a list containing strings and numbers is not possible.

        Note that the given list is changed and nothing is returned. Use
        `Copy List` first, if you need to preserve the list also in the original
        order.

        Starting from Robot Framework 7.4, the sorted list is also returned.
        """
        if isinstance(list_, list):
            list_.sort()
        else:
            list_ = sorted(list_)
        return list_

    def list_should_contain_value(
        self,
        list_: ListLike,
        value: object,
        msg: "str | None" = None,
        ignore_case: bool = False,
    ):
        """Fails if the ``value`` is not found from ``list``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        normalize = Normalizer(ignore_case).normalize
        if normalize(value) not in normalize(list_):
            report_error(f"{seq2str2(list_)} does not contain value '{value}'.", msg)

    def list_should_not_contain_value(
        self,
        list_: ListLike,
        value: object,
        msg: "str | None" = None,
        ignore_case: bool = False,
    ):
        """Fails if the ``value`` is found from ``list``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        normalize = Normalizer(ignore_case).normalize
        if normalize(value) in normalize(list_):
            report_error(f"{seq2str2(list_)} contains value '{value}'.", msg)

    def list_should_not_contain_duplicates(
        self,
        list_: Sequence,
        msg: "str | None" = None,
        ignore_case: bool = False,
    ):
        """Fails if any element in the ``list`` is found from it more than once.

        The default error message lists all the elements that were found
        from the ``list`` multiple times, but it can be overridden by giving
        a custom ``msg``. All multiple times found items and their counts are
        also logged.

        This keyword works with all iterables that can be converted to a list.
        The original iterable is never altered.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        dupes = []
        list_ = Normalizer(ignore_case).normalize(list_)
        for item in list_:
            if item not in dupes:
                count = list_.count(item)
                if count > 1:
                    logger.info(f"'{item}' found {count} times.")
                    dupes.append(item)
        if dupes:
            raise AssertionError(msg or f"{seq2str(dupes)} found multiple times.")

    def lists_should_be_equal(
        self,
        list1: ListLike,
        list2: ListLike,
        msg: "str | None" = None,
        values: bool = True,
        names: "Mapping[int, str] | Sequence[str] | None" = None,
        ignore_order: bool = False,
        ignore_case: bool = False,
    ):
        """Fails if given lists are unequal.

        The keyword first verifies that the lists have equal lengths, and then
        it checks are all their values equal. Possible differences between the
        values are listed in the default error message like ``Index 4: ABC !=
        Abc``. The types of the lists do not need to be the same. For example,
        Python tuple and list with same content are considered equal.

        The error message can be configured using ``msg`` and ``values``
        arguments:
        - If ``msg`` is not given, the default error message is used.
        - If ``msg`` is given and ``values`` gets a value considered true,
          the error message starts with the given
          ``msg`` followed by a newline and the default message.
        - If ``msg`` is given and ``values``  is not given a true value,
          the error message is just the given ``msg``.

        The optional ``names`` argument can be used for naming the indices
        shown in the default error message. It can either be a list of names
        matching the indices in the lists or a dictionary where keys are
        indices that need to be named. It is not necessary to name all indices.
        When using a dictionary, keys can be either integers
        or strings that can be converted to integers.

        Examples:
        | ${names} = | Create List | First Name | Family Name | Email |
        | Lists Should Be Equal | ${people1} | ${people2} | names=${names} |
        | ${names} = | Create Dictionary | 0=First Name | 2=Email |
        | Lists Should Be Equal | ${people1} | ${people2} | names=${names} |

        If the items in index 2 would differ in the above examples, the error
        message would contain a row like ``Index 2 (email): name@foo.com !=
        name@bar.com``.

        The optional ``ignore_order`` argument can be used to ignore the order
        of the elements in the lists. Using it requires items to be sortable.
        This option works recursively with nested lists starting from Robot
        Framework 7.0.

        Example:
        | ${list1} = | Create List | apple | cherry | banana |
        | ${list2} = | Create List | cherry | banana | apple |
        | Lists Should Be Equal | ${list1} | ${list2} | ignore_order=True |

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        values = deprecate_no_values(values)
        len1 = len(list1)
        len2 = len(list2)
        if len1 != len2:
            report_error(f"Lengths are different: {len1} != {len2}", msg, values)
        if not names:
            names = {}
        elif not isinstance(names, Mapping):
            names = dict(zip(range(len1), names))
        normalize = Normalizer(ignore_case, ignore_order=ignore_order).normalize
        diffs = list(self._yield_list_diffs(normalize(list1), normalize(list2), names))
        if diffs:
            report_error("Lists are different:\n" + "\n".join(diffs), msg, values)

    def _yield_list_diffs(
        self,
        list1: Sequence,
        list2: Sequence,
        names: "Mapping[int, str]",
    ) -> "Iterator[str]":
        for index, (item1, item2) in enumerate(zip(list1, list2)):
            name = f" ({names[index]})" if index in names else ""
            try:
                assert_equal(item1, item2, msg=f"Index {index}{name}")
            except AssertionError as err:
                yield str(err)

    def list_should_contain_sub_list(
        self,
        list1: ListLike,
        list2: ListLike,
        msg: "str | None" = None,
        values: bool = True,
        ignore_case: bool = False,
    ):
        """Fails if not all elements in ``list2`` are found in ``list1``.

        The order of values and the number of values are not taken into
        account.

        See `Lists Should Be Equal` for more information about configuring
        the error message with ``msg`` and ``values`` arguments.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        values = deprecate_no_values(values)
        normalize = Normalizer(ignore_case).normalize
        list1 = normalize(list1)
        list2 = normalize(list2)
        diffs = seq2str([item for item in list2 if item not in list1])
        if diffs:
            report_error(f"Following values are missing: {diffs}", msg, values)

    def log_list(self, list_: Sequence, level: logger.LogLevel = "INFO"):
        """Logs contents of the ``list`` using the given ``level``."""
        logger.write("\n".join(self._log_list(list_)), level)

    def _log_list(self, list_: "Sequence[object]") -> "Iterator[str]":
        if not list_:
            yield "List is empty."
        elif len(list_) == 1:
            yield "List has one item:"
            yield str(list_[0])
        else:
            yield f"List length is {len(list_)} and it contains following items:"
            for index, item in enumerate(list_):
                yield f"{index}: {item}"

    def _index_error(self, list_: Sequence, index: int) -> NoReturn:
        raise IndexError(f"Given index {index} is out of the range 0-{len(list_) - 1}.")


class _Dictionary:

    def convert_to_dictionary(self, item: object) -> dict:
        """Converts the given ``item`` to a Python ``dict`` type.

        Mainly useful for converting other mappings to normal dictionaries.
        This includes converting Robot Framework's own ``DotDict`` instances
        that it uses if variables are created using the ``&{var}`` syntax.

        Use `Create Dictionary` from the BuiltIn library for constructing new
        dictionaries.
        """
        return dict(item)  # type: ignore

    def set_to_dictionary(
        self,
        dictionary: MutableMapping,
        *key_value_pairs: object,
        **items: object,
    ) -> MutableMapping:
        """Adds the given ``key_value_pairs`` and/or ``items`` to the ``dictionary``.

        If given items already exist in the dictionary, their values are updated.

        The modified dictionary is also returned.

        It is easiest to specify items using the ``name=value`` syntax:
        | Set To Dictionary | ${D1} | key=value | second=${2} |
        =>
        | ${D1} = {'a': 1, 'key': 'value', 'second': 2}

        A limitation of the above syntax is that keys must be strings.
        That can be avoided by passing keys and values as separate arguments:
        | Set To Dictionary | ${D1} | key | value | ${2} | value 2 |
        =>
        | ${D1} = {'a': 1, 'key': 'value', 2: 'value 2'}

        Starting from Robot Framework 6.1, it is also possible to use the native
        item assignment syntax. This is equivalent to the above:
        | ${D1}[key] =  | Set Variable | value |
        | ${D1}[${2}] = | Set Variable | value 2 |
        """
        if len(key_value_pairs) % 2 != 0:
            raise ValueError(
                "Adding data to a dictionary failed. There should be even "
                "number of key-value-pairs."
            )
        for i in range(0, len(key_value_pairs), 2):
            dictionary[key_value_pairs[i]] = key_value_pairs[i + 1]
        dictionary.update(items)
        return dictionary

    def remove_from_dictionary(
        self,
        dictionary: MutableMapping,
        *keys: object,
    ) -> MutableMapping:
        """Removes the given ``keys`` from the ``dictionary``.

        If the given ``key`` does not exist in the ``dictionary``, it is ignored.

        Starting from Robot Framework 7.4, the modified dictionary is also returned.

        Example:
        | Remove From Dictionary | ${D3} | b | x | y |
        =>
        | ${D3} = {'a': 1, 'c': 3}
        """
        for key in keys:
            if key in dictionary:
                value = dictionary.pop(key)
                logger.info(f"Removed item with key '{key}' and value '{value}'.")
            else:
                logger.info(f"Key '{key}' not found.")
        return dictionary

    def pop_from_dictionary(
        self,
        dictionary: MutableMapping,
        key: object,
        default: object = NOT_SET,
    ) -> object:
        """Pops the given ``key`` from the ``dictionary`` and returns its value.

        The keyword fails if the given ``key`` cannot be found from the ``dictionary``
        by default. If optional ``default`` value is given, it will be returned instead.

        Example:
        | ${val}= | Pop From Dictionary | ${D3} | b |
        =>
        | ${val} = 2
        | ${D3} = {'a': 1, 'c': 3}
        """
        if default is NOT_SET:
            self.dictionary_should_contain_key(dictionary, key)
            return dictionary.pop(key)
        return dictionary.pop(key, default)

    def keep_in_dictionary(
        self,
        dictionary: MutableMapping,
        *keys: object,
    ) -> MutableMapping:
        """Keeps the given ``keys`` in the ``dictionary`` and removes all others.

        If the given ``key`` does not exist in the ``dictionary``, it is ignored.

        Starting from Robot Framework 7.4, the modified dictionary is also returned.

        Example:
        | Keep In Dictionary | ${D5} | b | x | d |
        =>
        | ${D5} = {'b': 2, 'd': 4}
        """
        remove_keys = [k for k in dictionary if k not in keys]
        self.remove_from_dictionary(dictionary, *remove_keys)
        return dictionary

    def copy_dictionary(
        self,
        dictionary: Mapping,
        deepcopy: bool = False,
    ) -> Mapping:
        """Returns a copy of the given dictionary.

        By default, returns a new dictionary with same items as in the original.
        Set the ``deepcopy`` argument to a true value if also items should
        be copied.

        The given dictionary is never altered by this keyword.
        """
        if deepcopy:
            return copy.deepcopy(dictionary)
        return copy.copy(dictionary)

    def get_dictionary_keys(
        self,
        dictionary: Mapping,
        sort_keys: bool = True,
    ) -> "list[object]":
        """Returns keys of the given ``dictionary`` as a list.

        By default, keys are returned in sorted order (assuming they are
        sortable), but they can be returned in the original order by giving
        ``sort_keys`` a false value.

        The given ``dictionary`` is never altered by this keyword.

        Example:
        | ${sorted} =   | Get Dictionary Keys | ${D3} |
        | ${unsorted} = | Get Dictionary Keys | ${D3} | sort_keys=False |
        """
        if sort_keys:
            try:
                return sorted(dictionary)
            except TypeError:
                pass
        return list(dictionary)

    def get_dictionary_values(
        self,
        dictionary: Mapping,
        sort_keys: bool = True,
    ) -> "list[object]":
        """Returns values of the given ``dictionary`` as a list.

        Uses `Get Dictionary Keys` to get keys and then returns corresponding
        values. By default, keys are sorted and values returned in that order,
        but this can be changed by giving ``sort_keys`` a false value.

        The given ``dictionary`` is never altered by this keyword.

        Example:
        | ${sorted} =   | Get Dictionary Values | ${D3} |
        | ${unsorted} = | Get Dictionary Values | ${D3} | sort_keys=False |
        """
        keys = self.get_dictionary_keys(dictionary, sort_keys=sort_keys)
        return [dictionary[k] for k in keys]

    def get_dictionary_items(
        self,
        dictionary: Mapping,
        sort_keys: bool = True,
    ) -> "list[tuple[object, object]]":
        """Returns items of the given ``dictionary`` as a list.

        Uses `Get Dictionary Keys` to get keys and then returns corresponding
        items. By default, keys are sorted and items returned in that order,
        but this can be changed by giving ``sort_keys`` a false value.

        Items are returned as a flat list so that first item is a key,
        second item is a corresponding value, third item is the second key,
        and so on.

        The given ``dictionary`` is never altered by this keyword.

        Example:
        | ${sorted} =   | Get Dictionary Items | ${D3} |
        | ${unsorted} = | Get Dictionary Items | ${D3} | sort_keys=False |
        """
        keys = self.get_dictionary_keys(dictionary, sort_keys=sort_keys)
        return [i for key in keys for i in (key, dictionary[key])]

    def get_from_dictionary(
        self,
        dictionary: Mapping,
        key: object,
        default: object = NOT_SET,
    ) -> object:
        """Returns a value from the given ``dictionary`` based on the given ``key``.

        If the given ``key`` cannot be found from the ``dictionary``, this
        keyword fails. If optional ``default`` value is given, it will be
        returned instead of failing.

        The given dictionary is never altered by this keyword.

        Example:
        | ${value} = | Get From Dictionary | ${D3} | b |
        =>
        | ${value} = 2

        Support for ``default`` is new in Robot Framework 6.0.
        """
        try:
            return dictionary[key]
        except KeyError:
            if default is not NOT_SET:
                return default
            raise RuntimeError(f"Dictionary does not contain key '{key}'.")

    def dictionary_should_contain_key(
        self,
        dictionary: Mapping,
        key: object,
        msg: "str | None" = None,
        ignore_case: IgnoreCase = False,
    ):
        """Fails if ``key`` is not found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        norm = Normalizer(ignore_case)
        if norm.normalize_key(key) not in norm.normalize(dictionary):
            report_error(f"Dictionary does not contain key '{key}'.", msg)

    def dictionary_should_not_contain_key(
        self,
        dictionary: Mapping,
        key: object,
        msg: "str | None" = None,
        ignore_case: IgnoreCase = False,
    ):
        """Fails if ``key`` is found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        norm = Normalizer(ignore_case)
        if norm.normalize_key(key) in norm.normalize(dictionary):
            report_error(f"Dictionary contains key '{key}'.", msg)

    def dictionary_should_contain_item(
        self,
        dictionary: Mapping,
        key: object,
        value: object,
        msg: "str | None" = None,
        ignore_case: IgnoreCase = False,
    ):
        """An item of ``key`` / ``value`` must be found in a ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        self.dictionary_should_contain_key(dictionary, key, msg, ignore_case)  # type: ignore
        norm = Normalizer(ignore_case)
        assert_equal(
            norm.normalize(dictionary)[norm.normalize_key(key)],
            norm.normalize_value(value),
            msg or f"Value of dictionary key '{key}' does not match",
            values=not msg,
        )

    def dictionary_should_contain_value(
        self,
        dictionary: Mapping,
        value: object,
        msg: "str | None" = None,
        ignore_case: IgnoreCase = False,
    ):
        """Fails if ``value`` is not found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        norm = Normalizer(ignore_case)
        if norm.normalize_value(value) not in norm.normalize(dictionary).values():
            report_error(f"Dictionary does not contain value '{value}'.", msg)

    def dictionary_should_not_contain_value(
        self,
        dictionary: Mapping,
        value: object,
        msg: "str | None" = None,
        ignore_case: IgnoreCase = False,
    ):
        """Fails if ``value`` is found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.
        """
        norm = Normalizer(ignore_case)
        if norm.normalize_value(value) in norm.normalize(dictionary).values():
            report_error(f"Dictionary contains value '{value}'.", msg)

    def dictionaries_should_be_equal(
        self,
        dict1: Mapping,
        dict2: Mapping,
        msg: "str | None" = None,
        values: bool = True,
        ignore_keys: "Sequence | None" = None,
        ignore_case: IgnoreCase = False,
        ignore_value_order: bool = False,
    ):
        """Fails if the given dictionaries are not equal.

        First the equality of dictionaries' keys is checked and after that all
        the key value pairs. If there are differences between the values, those
        are listed in the error message. The types of the dictionaries do not
        need to be same.

        ``ignore_keys`` can be used to provide a list of keys to ignore in the
        comparison. This option is new in Robot Framework 6.1. It works recursively
        with nested dictionaries starting from Robot Framework 7.0.

        Examples:
        | Dictionaries Should Be Equal | ${dict} | ${expected} |
        | Dictionaries Should Be Equal | ${dict} | ${expected} | ignore_keys=${ignored} |
        | Dictionaries Should Be Equal | ${dict} | ${expected} | ignore_keys=['key1', 'key2'] |

        See `Lists Should Be Equal` for more information about configuring
        the error message with ``msg`` and ``values`` arguments.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.

        The ``ignore_value_order`` argument can be used to make comparison in case of
        list-like values to ignore the order of the elements in the lists.
        Using it requires items to be sortable.
        This option is new in Robot Framework 7.2.
        """
        values = deprecate_no_values(values)
        normalize = Normalizer(
            ignore_case=ignore_case,
            ignore_keys=ignore_keys,
            ignore_order=ignore_value_order,
        ).normalize
        dict1 = normalize(dict1)
        dict2 = normalize(dict2)
        self._should_have_same_keys(dict1, dict2, msg, values)
        self._should_have_same_values(dict1, dict2, msg, values)

    def _should_have_same_keys(
        self,
        dict1: Mapping,
        dict2: Mapping,
        message: "str | None",
        values: bool,
        validate_both: bool = True,
    ):
        missing = seq2str([k for k in dict2 if k not in dict1])
        error = ""
        if missing:
            error = f"Following keys missing from first dictionary: {missing}"
        if validate_both:
            missing = seq2str([k for k in dict1 if k not in dict2])
            if missing:
                error += f"\nFollowing keys missing from second dictionary: {missing}"
        if error:
            report_error(error.strip(), message, values)

    def _should_have_same_values(
        self,
        dict1: Mapping,
        dict2: Mapping,
        message: "str | None",
        values: bool,
    ):
        errors = []
        for key in dict2:
            try:
                assert_equal(dict1[key], dict2[key], msg=f"Key {key}")
            except AssertionError as err:
                errors.append(str(err))
        if errors:
            error = "\n".join(["Following keys have different values:", *errors])
            report_error(error, message, values)

    def dictionary_should_contain_sub_dictionary(
        self,
        dict1: Mapping,
        dict2: Mapping,
        msg: "str | None" = None,
        values: bool = True,
        ignore_case: IgnoreCase = False,
        ignore_value_order: bool = False,
    ):
        """Fails unless all items in ``dict2`` are found from ``dict1``.

        See `Lists Should Be Equal` for more information about configuring
        the error message with ``msg`` and ``values`` arguments.

        The ``ignore_case`` argument can be used to make comparison case-insensitive.
        See the `Ignore case` section for more details. This option is new in
        Robot Framework 7.0.

        The ``ignore_value_order`` argument can be used to make comparison in case of
        list-like values to ignore the order of the elements in the lists.
        Using it requires items to be sortable.
        This option is new in Robot Framework 7.2.
        """
        values = deprecate_no_values(values)
        normalizer = Normalizer(
            ignore_case=ignore_case,
            ignore_order=ignore_value_order,
        )
        dict1 = normalizer.normalize(dict1)
        dict2 = normalizer.normalize(dict2)
        self._should_have_same_keys(dict1, dict2, msg, values, validate_both=False)
        self._should_have_same_values(dict1, dict2, msg, values)

    def log_dictionary(
        self,
        dictionary: Mapping,
        level: logger.LogLevel = "INFO",
    ):
        """Logs the contents of the ``dictionary`` using the given ``level``."""
        logger.write("\n".join(self._log_dictionary(dictionary)), level)

    def _log_dictionary(
        self,
        dictionary: Mapping,
    ) -> "Iterator[str]":
        if not dictionary:
            yield "Dictionary is empty."
        elif len(dictionary) == 1:
            yield "Dictionary has one item:"
        else:
            yield f"Dictionary size is {len(dictionary)} and it contains following items:"
        for key in self.get_dictionary_keys(dictionary):
            yield f"{key}: {dictionary[key]}"


class Collections(_List, _Dictionary):
    """A library providing keywords for handling lists and dictionaries.

    ``Collections`` is Robot Framework's standard library that provides a
    set of keywords for handling Python lists and dictionaries. This
    library has keywords, for example, for modifying and getting
    values from lists and dictionaries (e.g. `Append To List`, `Get
    From Dictionary`) and for verifying their contents (e.g. `Lists
    Should Be Equal`, `Dictionary Should Contain Value`).

    == Table of contents ==

    %TOC%

    = Related keywords in BuiltIn =

    Following keywords in the BuiltIn library can also be used with
    lists and dictionaries:

    | = Keyword Name =             | = Applicable With = |
    | `Create List`                | lists |
    | `Create Dictionary`          | dicts |
    | `Get Length`                 | both  |
    | `Length Should Be`           | both  |
    | `Should Be Empty`            | both  |
    | `Should Not Be Empty`        | both  |
    | `Should Contain`             | both  |
    | `Should Not Contain`         | both  |
    | `Should Contain X Times`     | lists |
    | `Should Not Contain X Times` | lists |
    | `Get Count`                  | lists |

    = Using with list-like and dictionary-like objects =

    List related keywords can in general be used with tuples and other sequences,
    not only with ``list`` objects. List keywords that validate something typically
    even work with sets and mappings (with mappings they look only at keys).
    If keywords that modify lists are used with immutable sequences such as tuples,
    values are automatically converted to lists. In such cases the original value
    obviously is not mutated, but these keywords also return the modified value
    and that can be used instead.

    Dictionary related keywords also generally work with any mapping, not only
    with ``dict`` objects. If keywords that modify dictionaries are used with
    immutable mappings, values are automatically converted to dictionaries.
    Original values cannot be modified in these cases either, but modified values
    are returned and can be used instead.

    What values each keyword actually accepts can be seen from argument types
    and keyword documentation.

    Returning values from keywords that modify lists or dictionaries is new
    in Robot Framework 7.4. With earlier version these keywords could only
    be used with mutable values.

    = Ignore case =

    Various keywords support ignoring case in comparisons by using the optional
    ``ignore_case`` argument. Case-insensitivity can be enabled by using
    ``ignore_case=True`` and it works recursively.

    With dictionaries, it is also possible to use special values ``KEYS`` and
    ``VALUES`` to normalize only keys or values, respectively. These options
    themselves are case-insensitive and also singular forms ``KEY`` and
    ``VALUE`` are supported.

    If a dictionary contains keys that normalize to the same value, e.g.
    ``{'a': 1, 'A': 2}``, normalizing keys causes an error.

    Examples:
    | `Lists Should Be Equal`        | ${list1} | ${list2} | ignore_case=True   |
    | `Dictionaries Should Be Equal` | ${dict1} | ${dict2} | ignore_case=VALUES |

    Notice that some keywords accept also an older ``case_insensitive`` argument
    in addition to ``ignore_case``. The latter is new in Robot Framework 7.0 and
    should be used unless there is a need to support older versions. The old
    argument is considered deprecated and will eventually be removed.

    Starting from Robot Framework 7.4, case-insensitivity works also with
    bytes, not only with strings.

    = Data in examples =

    List related keywords use variables in format ``${Lx}`` in their examples.
    They mean lists with as many alphabetic characters as specified by ``x``.
    For example, ``${L1}`` means ``['a']`` and ``${L3}`` means
    ``['a', 'b', 'c']``.

    Dictionary keywords use similar ``${Dx}`` variables. For example, ``${D1}``
    means ``{'a': 1}`` and ``${D3}`` means ``{'a': 1, 'b': 2, 'c': 3}``.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = get_version()

    def should_contain_match(
        self,
        list: ListLike,
        pattern: str,
        msg: "str | None" = None,
        case_insensitive: "bool | None" = None,
        whitespace_insensitive: "bool | None" = None,
        ignore_case: bool = False,
        ignore_whitespace: bool = False,
    ):
        """Fails if ``pattern`` is not found in ``list``.

        By default, pattern matching is similar to matching files in a shell
        and is case-sensitive and whitespace-sensitive. In the pattern syntax,
        ``*`` matches to anything and ``?`` matches to any single character. You
        can also prepend ``glob=`` to your pattern to explicitly use this pattern
        matching behavior.

        If you prepend ``regexp=`` to your pattern, your pattern will be used
        according to the Python
        [http://docs.python.org/library/re.html|re module] regular expression
        syntax. Notice that the backslash character often used with regular
        expressions is an escape character in Robot Framework data and needs
        to be escaped with another backslash like ``regexp=\\\\d{6}``. See
        `BuiltIn.Should Match Regexp` for more details.

        Matching is case-sensitive by default, but that can be changed by giving
        the ``ignore_case`` argument a true value.
        This argument is new in Robot Framework 7.0, but with earlier versions
        it is possible to use ``case_insensitive`` for the same purpose.

        It is possible to ignore all whitespace by giving the ``ignore_whitespace``
        argument a true value. This argument is new in Robot Framework 7.0 as well,
        and with earlier versions it is possible to use ``whitespace_insensitive``.

        Notice that both ``case_insensitive`` and ``whitespace_insensitive``
        are considered deprecated. They will eventually be removed.

        Non-string values in lists are ignored when matching patterns.

        Use the ``msg`` argument to override the default error message.

        Examples:
        | Should Contain Match | ${list} | a*              | | | # Match strings beginning with 'a'. |
        | Should Contain Match | ${list} | regexp=a.*      | | | # Same as the above but with regexp. |
        | Should Contain Match | ${list} | regexp=\\\\d{6} | | | # Match strings containing six digits. |
        | Should Contain Match | ${list} | a*  | ignore_case=True       | | # Match strings beginning with 'a' or 'A'. |
        | Should Contain Match | ${list} | ab* | ignore_whitespace=yes  | | # Match strings beginning with 'ab' with possible whitespace ignored. |
        | Should Contain Match | ${list} | ab* | ignore_whitespace=true | ignore_case=true | # Same as the above but also ignore case. |
        """
        matches = self._get_matches(
            sequence=list,
            pattern=pattern,
            case_insensitive=case_insensitive,
            whitespace_insensitive=whitespace_insensitive,
            ignore_case=ignore_case,
            ignore_whitespace=ignore_whitespace,
        )
        if not matches:
            list = seq2str2(list)
            report_error(f"{list} does not contain match for pattern '{pattern}'.", msg)

    def should_not_contain_match(
        self,
        list: ListLike,
        pattern: str,
        msg: "str | None" = None,
        case_insensitive: "bool | None" = None,
        whitespace_insensitive: "bool | None" = None,
        ignore_case: bool = False,
        ignore_whitespace: bool = False,
    ):
        """Fails if ``pattern`` is found in ``list``.

        Exact opposite of `Should Contain Match` keyword. See that keyword
        for information about arguments and usage in general.
        """
        matches = self._get_matches(
            sequence=list,
            pattern=pattern,
            case_insensitive=case_insensitive,
            whitespace_insensitive=whitespace_insensitive,
            ignore_case=ignore_case,
            ignore_whitespace=ignore_whitespace,
        )
        if matches:
            list = seq2str2(list)
            report_error(f"{list} contains match for pattern '{pattern}'.", msg)

    def get_matches(
        self,
        list: ListLike,
        pattern: str,
        case_insensitive: "bool | None" = None,
        whitespace_insensitive: "bool | None" = None,
        ignore_case: bool = False,
        ignore_whitespace: bool = False,
    ) -> "list[str]":
        """Returns a list of matches to ``pattern`` in ``list``.

        For more information on ``pattern``, ``case_insensitive/ignore_case``, and
        ``whitespace_insensitive/ignore_whitespace``, see `Should Contain Match`.

        Examples:
        | ${matches}= | Get Matches | ${list} | a* | # ${matches} will contain any string beginning with 'a' |
        | ${matches}= | Get Matches | ${list} | regexp=a.* | # ${matches} will contain any string beginning with 'a' (regexp version) |
        | ${matches}= | Get Matches | ${list} | a* | ignore_case=True | # ${matches} will contain any string beginning with 'a' or 'A' |
        """
        return self._get_matches(
            sequence=list,
            pattern=pattern,
            case_insensitive=case_insensitive,
            whitespace_insensitive=whitespace_insensitive,
            ignore_case=ignore_case,
            ignore_whitespace=ignore_whitespace,
        )

    def get_match_count(
        self,
        list: ListLike,
        pattern: str,
        case_insensitive: "bool | None" = None,
        whitespace_insensitive: "bool | None" = None,
        ignore_case: bool = False,
        ignore_whitespace: bool = False,
    ) -> int:
        """Returns the count of matches to ``pattern`` in ``list``.

        For more information on ``pattern``, ``case_insensitive/ignore_case``, and
        ``whitespace_insensitive/ignore_whitespace``, see `Should Contain Match`.

        Examples:
        | ${count}= | Get Match Count | ${list} | a* | # ${count} will be the count of strings beginning with 'a' |
        | ${count}= | Get Match Count | ${list} | regexp=a.* | # ${matches} will be the count of strings beginning with 'a' (regexp version) |
        | ${count}= | Get Match Count | ${list} | a* | case_insensitive=${True} | # ${matches} will be the count of strings beginning with 'a' or 'A' |
        """
        matches = self.get_matches(
            list=list,
            pattern=pattern,
            case_insensitive=case_insensitive,
            whitespace_insensitive=whitespace_insensitive,
            ignore_case=ignore_case,
            ignore_whitespace=ignore_whitespace,
        )
        return len(matches)

    def _get_matches(
        self,
        sequence: Sequence,
        pattern: str,
        case_insensitive: "bool | None" = None,
        whitespace_insensitive: "bool | None" = None,
        ignore_case: bool = True,
        ignore_whitespace: bool = False,
    ) -> "list[str]":
        # `ignore_xxx` were added in RF 7.0 for consistency reasons.
        # The idea is that they eventually replace `xxx_insensitive`.
        # TODO: Emit deprecation warnings in RF 8.0.
        if case_insensitive is not None:
            ignore_case = case_insensitive
        if whitespace_insensitive is not None:
            ignore_whitespace = whitespace_insensitive
        if not isinstance(pattern, str):
            raise TypeError(f"Pattern must be string, got '{type_name(pattern)}'.")
        regexp = False
        if pattern.startswith("regexp="):
            pattern = pattern[7:]
            regexp = True
        elif pattern.startswith("glob="):
            pattern = pattern[5:]
        matcher = Matcher(
            pattern,
            caseless=ignore_case,
            spaceless=ignore_whitespace,
            regexp=regexp,
        )
        return [s for s in sequence if isinstance(s, str) and matcher.match(s)]


def deprecate_no_values(values: "bool | str") -> bool:
    # Deprecated in RF 7.4. TODO: Remove in RF 9.
    if isinstance(values, str) and values.upper() == "NO VALUES":
        logger.warn(
            f"Using '{values}' for disabling the 'values' argument is deprecated. "
            f"Use 'values=False' instead."
        )
        return False
    return bool(values)


def report_error(default: str, message: "str | None", values: bool = False) -> NoReturn:
    if not message:
        message = default
    elif values:
        message += "\n" + default
    raise AssertionError(message)
