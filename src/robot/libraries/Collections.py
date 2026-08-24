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
        """Converts the given `item` to a Python `list` type.

        Args:
            item: The item to convert to a list.

        Returns:
            The converted list.

        Mainly useful for converting tuples and other iterable to lists.
        Use [Create List] from the BuiltIn library for constructing new lists.

        Use [Split String To Characters] from the String library for splitting
        strings to a list of characters.
        """
        return list(item)  # type: ignore

    def append_to_list(
        self,
        list_: MutableSequence,
        *values: object,
    ) -> MutableSequence:
        """Adds `values` to the end of `list`.

        Args:
            list_: The list to modify.
            *values: Values to append.

        Returns:
            The modified list.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Append to list
           ${list_1} =    Copy List    ${LIST_ABC}
           ${list_2} =    Copy List    ${LIST_ABCDE}
           ${appended_1} =    Append To List    ${list_1}    xxx
           ${appended_2} =    Append To List    ${list_2}    x    y    z
           Should Be Equal    ${appended_1}    ["a", "b", "c", "xxx"]    type=list
           Should Be Equal    ${appended_2}    ["a", "b", "c", "d", "e", "x", "y", "z"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        list_.extend(values)
        return list_

    def insert_into_list(
        self,
        list_: MutableSequence,
        index: int,
        value: object,
    ) -> MutableSequence:
        """Inserts `value` into `list` to the position specified with `index`.

        Args:
            list_: The list to modify.
            index: Index where to insert the value.
            value: The value to insert.

        Returns:
            The modified list.

        Index `0` adds the value into the first position, `1` to the second,
        and so on. Inserting from right works with negative indices so that
        `-1` is the second last position, `-2` third last, and so on. Use
        [Append To List] to add items to the end of the list.

        If the absolute value of the index is greater than
        the length of the list, the value is added at the end
        (positive index) or the beginning (negative index).

        Starting from Robot Framework 7.4, the modified list is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Insert in list
            ${list_1} =    Copy List    ${LIST_ABC}
            ${list_2} =    Copy List    ${LIST_ABC}
            ${inserted_1} =    Insert Into List    ${list_1}    0    xxx
            ${inserted_2} =    Insert Into List    ${list_2}    -1    xxx
            Should Be Equal    ${inserted_1}    ["xxx", "a", "b", "c"]    type=list
            Should Be Equal    ${inserted_2}    ["a", "b", "xxx", "c"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        list_.insert(index, value)
        return list_

    def combine_lists(self, *lists: ListLike) -> list:
        """Combines the given `lists` together and returns the result.

        Args:
            *lists: Lists to combine.

        Returns:
            A new list containing all items.

        The given lists are not altered by this keyword.

        Examples:

        ```robotframework
        *** Test Cases ***
        Combine lists
            ${combined} =    Combine Lists    ${LIST_ABC}    ${LIST_ABCDE}
            Should Be Equal    ${combined}    ["a", "b", "c", "a", "b", "c", "d", "e"]    type=list
        ```
        """
        return list(chain.from_iterable(lists))

    def set_list_value(
        self,
        list_: MutableSequence,
        index: int,
        value: object,
    ) -> MutableSequence:
        """Sets the value of `list` specified by `index` to the given `value`.

        Args:
            list_: The list to modify.
            index: Index of the value to set.
            value: The new value.

        Returns:
            The modified list.

        Raises:
            IndexError: If `index` is out of range.

        Index `0` means the first position, `1` the second and so on.
        Similarly, `-1` is the last position, `-2` second last, and so on.
        Using an index that does not exist on the list causes an error.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Set list value
            ${list_1} =    Copy List    ${LIST_ABC}
            ${list_2} =    Copy List    ${LIST_ABC}
            ${set_1} =    Set List Value    ${list_1}    1    xxx
            ${set_2} =    Set List Value    ${list_2}    -1    yyy
            Should Be Equal    ${set_1}    ["a", "xxx", "c"]    type=list
            Should Be Equal    ${set_2}    ["a", "b", "yyy"]    type=list
        ```

        Starting from Robot Framework 6.1, it is also possible to use the native
        item assignment syntax instead of this keyword. This is equivalent to
        the above:

        ```robotframework
        *** Test Cases ***
        Set list value using item assignment syntax
            ${list_1} =    Copy List    ${LIST_ABC}
            ${list_2} =    Copy List    ${LIST_ABC}
            ${list_1}[1] =    Set Variable    xxx
            ${list_2}[-1] =    Set Variable    yyy
            Should Be Equal    ${list_1}    ["a", "xxx", "c"]    type=list
            Should Be Equal    ${list_2}    ["a", "b", "yyy"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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
        """Removes all occurrences of given `values` from `list`.

        Args:
            list_: The list to modify.
            *values: Values to remove.

        Returns:
            The modified list.

        It is not an error if a value does not exist in the list at all.

        Starting from Robot Framework 7.4, the modified list is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Remove values from list
            ${list_1} =    Copy List    ${LIST_ABCDE}
            ${removed} =    Remove Values From List    ${list_1}    a    c    e    f
            Should Be Equal    ${removed}    ["b", "d"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        for value in values:
            while value in list_:
                list_.remove(value)
        return list_

    def remove_from_list(self, list_: MutableSequence, index: int) -> object:
        """Removes and returns the value specified with an `index` from `list`.

        Args:
            list_: The list to modify.
            index: Index of the value to remove.

        Returns:
            The removed value.

        Raises:
            IndexError: If `index` is out of range.

        Index `0` means the first position, `1` the second and so on.
        Similarly, `-1` is the last position, `-2` the second last, and so on.
        Using an index that does not exist on the list causes an error.

        Examples:

        ```robotframework
        *** Test Cases ***
        Remove from list
            ${list_1} =    Copy List    ${LIST_ABC}
            ${removed} =    Remove From List    ${list_1}    0
            Should Be Equal    ${list_1}    ["b", "c"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        try:
            return list_.pop(index)
        except IndexError:
            self._index_error(list_, index)

    def remove_duplicates(self, list_: Sequence) -> list:
        """Returns a list without duplicates based on the given `list`.

        Args:
            list_: The list to remove duplicates from.

        Returns:
            A new list without duplicates.

        Creates and returns a new list that contains all items in the given
        list so that one item can appear only once. Order of the items in
        the new list is the same as in the original except for missing
        duplicates. Number of the removed duplicates is logged.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        ret = []
        for item in list_:
            if item not in ret:
                ret.append(item)
        removed = len(list_) - len(ret)
        logger.info(f"{removed} duplicate{s(removed)} removed.")
        return ret

    def get_from_list(self, list_: Sequence, index: int) -> object:
        """Returns the value specified with an `index` from `list`.

        Args:
            list_: The list to get a value from.
            index: Index of the value to get.

        Returns:
            The value at the given index.

        Raises:
            IndexError: If `index` is out of range.

        Index `0` means the first position, `1` the second, and so on.
        Negative indices work so that `-1` is the last position, `-2`
        the second last, and so on. Using an index that does not exist on
        the list causes an error.

        Examples (including Python equivalents in comments):

        ```robotframework
        *** Test Cases ***
        Get from list
            ${list_1} =    Copy List    ${LIST_ABCDE}
            ${item_1} =    Get From List    ${list_1}    0     # list_1[0]
            ${item_2} =    Get From List    ${list_1}    -2    # list_1[-2]
            Should Be Equal    ${item_1}    a
            Should Be Equal    ${item_2}    d
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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
        """Returns a slice of the given list between `start` and `end` indices.

        Args:
            list_: The list to get a slice from.
            start: Start index of the slice.
            end: End index of the slice.

        Returns:
            The requested slice.

        Indices have the same semantics as with [Get From List]. A difference is
        that too big or small indices are considered to be the same as the biggest
        or smallest valid indices, respectively, instead of causing an error.

        The item matching the start index is included in the returned slice, but
        the item matching the end index is not.

        To get all items from the beginning, use `0` (default) as the start index.
        To get all items until and including the end, use `None` (default) or
        list's length as the end index.

        Examples (incl. Python equivalents in comments):

        ```robotframework
        *** Test Cases ***
        Get slice from list
            ${list_1} =    Copy List    ${LIST_ABCDE}
            ${slice_1} =    Get Slice From List    ${list_1}    2    4    # list_1[2:4]
            ${slice_2} =    Get Slice From List    ${list_1}    1         # list_1[1:]
            ${slice_3} =    Get Slice From List    ${list_1}    end=-2    # list_1[0:-2]
            Should Be Equal    ${slice_1}    ["c", "d"]    type=list
            Should Be Equal    ${slice_2}    ["b", "c", "d", "e"]    type=list
            Should Be Equal    ${slice_3}    ["a", "b", "c"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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
        """Returns the number of occurrences of the given `value` in `list`.

        Args:
            list_: The list to search the value from.
            value: The value to search for.
            start: Optional start index for the search.
            end: Optional end index for the search.

        Returns:
            The number of occurrences.

        The search can be narrowed to the selected sublist by the `start` and
        `end` indexes having the same semantics as with [Get Slice From List]
        keyword.

        Examples:

        ```robotframework
        *** Test Cases ***
        Count values in list
            ${list_1} =   Copy List    ${LIST_ABC}
            ${count} =    Count Values In List    ${list_1}    b
            Should Be Equal    ${count}    ${1}
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        return self.get_slice_from_list(list_, start, end).count(value)

    def get_index_from_list(
        self,
        list_: Sequence,
        value: object,
        start: "int | Literal['']" = 0,
        end: "int | None" = None,
    ) -> int:
        """Returns the index of the first occurrence of the `value` on the list.

        Args:
            list_: The list to search the value from.
            value: The value to search ofr.
            start: Optional start index for the search.
            end: Optional end index for the search.

        Returns:
            The index of the value, or `-1` if not found.

        The search can be narrowed to the selected sublist by the `start` and
        `end` indexes having the same semantics as with [Get Slice From List]
        keyword. The returned index is always the index of the value in the
        original list.

        Examples:

        ```robotframework
        *** Test Cases ***
        Get index from list
            ${list_1} =    Copy List    ${LIST_ABCDE}
            ${index} =    Get Index From List    ${list_1}    d    start=1
            Should Be Equal    ${index}    ${3}
        ```

        Starting from Robot Framework 7.5, the returned index is always positive
        if the value is found. With earlier versions negative start indices
        yielded negative return values making it impossible to know did `-1`
        mean that the value had that index or that the value was not found.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        if start == "":
            # Deprecated in RF 7.4. TODO: Remove in RF 9.
            logger.warn(
                "Using an empty string as a start index with the 'Get Index From List' "
                "keyword is deprecated. Use '0' instead."
            )
            start = 0
        if start < 0:
            increment = max(start + len(list_), 0)
        else:
            increment = start
        list_ = self.get_slice_from_list(list_, start, end)
        try:
            return list_.index(value) + increment
        except ValueError:
            return -1

    def copy_list(self, list_: Sequence, deepcopy: bool = False) -> Sequence:
        """Returns a copy of the given list.

        Args:
            list_: The list to copy.
            deepcopy: Whether to also copy items.

        Returns:
            A copy of the list.

        By default, returns a new list with same items as in the original.
        Set the `deepcopy` argument to a true value if also items should
        be copied.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        if deepcopy:
            return copy.deepcopy(list_)
        return list_[:]

    def reverse_list(self, list_: MutableSequence) -> MutableSequence:
        """Reverses the given list.

        Args:
            list_: The list to reverse.

        Returns:
            The reversed list.

        Starting from Robot Framework 7.4, the reversed list is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Reverse list
            ${list_1} =    Copy List    ${LIST_ABC}
            ${reversed} =    Reverse List    ${list_1}
            Should Be Equal    ${reversed}    ["c", "b", "a"]    type=list
        ```

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        list_.reverse()
        return list_

    def sort_list(self, list_: MutableSequence) -> MutableSequence:
        """Sorts the given list.

        Args:
            list_: The list to sort.

        Returns:
            The sorted list.

        Raises:
            TypeError: If items are not comparable.

        Sorting fails if items in the list are not comparable with each others.
        For example, sorting a list containing strings and numbers is not possible.

        Starting from Robot Framework 7.4, the sorted list is also returned.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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
        """Fails if the `value` is not found from `list`.

        Args:
            list_: The list to verify.
            value: The value that should be found.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
        Robot Framework 7.0.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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
        """Fails if the `value` is found from `list`.

        Args:
            list_: The list to verify.
            value: The value that should not be found.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
        Robot Framework 7.0.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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
        """Fails if any element in the `list` is found from it more than once.

        Args:
            list_: The list to verify.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The default error message lists all the elements that were found
        from the `list` multiple times, but it can be overridden by giving
        a custom `msg`. All multiple times found items and their counts are
        also logged.

        This keyword works with all iterables that can be converted to a list.
        The original iterable is never altered.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
        Robot Framework 7.0.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
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

        Args:
            list1: The first list.
            list2: The second list.
            msg: Optional custom error message.
            values: When true, the default error message is added at the end of
              the possible custom error message.
            names: Optional names for indices shown in the error message.
            ignore_order: Whether to ignore the order of elements.
            ignore_case: Whether to ignore case in comparison.

        The keyword first verifies that the lists have equal lengths, and then
        it checks are all their values equal. Possible differences between the
        values are listed in the default error message like `Index 4: ABC !=
        Abc`. The types of the lists do not need to be the same. For example,
        Python tuple and list with same content are considered equal.

        The error message can be configured using `msg` and `values` arguments:

        - If `msg` is not given, the default error message is used.
        - If `msg` is given and `values` gets a value considered true,
          the error message starts with the given `msg` followed by
          a newline and the default message.
        - If `msg` is given and `values`  is not given a true value,
          the error message is just the given `msg`.

        The optional `names` argument can be used for naming the indices
        shown in the default error message. It can either be a list of names
        matching the indices in the lists or a dictionary where keys are
        indices that need to be named. It is not necessary to name all indices.
        When using a dictionary, keys can be either integers
        or strings that can be converted to integers.

        Examples:

        ```robotframework
        *** Variables ***
        @{USER1}         Jane    Doe    jane@example.com
        @{USER2}         John    Doe    john@example.com

        *** Test Cases ***
        Names as list
            VAR    @{names}    First Name    Family Name    Email
            Lists Should Be Equal    ${USER1}    ${USER2}    names=${names}

        Names as dict
            VAR    &{names}    0=First Name    1=Family Name    2=Email
            Lists Should Be Equal    ${USER1}    ${USER2}    names=${names}
        ```

        Both of the above examples fail with this message:

            Lists are different:
            Index 0 (First Name): Jane != John
            Index 2 (Email): jane@example.com != john@example.com

        The optional `ignore_order` argument can be used to ignore the order
        of the elements in the lists. Using it requires items to be sortable.
        This option works recursively with nested lists starting from Robot
        Framework 7.0.

        Examples:

        ```robotframework
        *** Test Cases ***
        Lists should be equal ignoring order
            VAR    @{list1}    apple     cherry    banana
            VAR    @{list2}    cherry    banana    apple
            Lists Should Be Equal    ${list}    ${list}    ignore_order=True
        ```

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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
        """Fails if not all elements in `list2` are found in `list1`.

        Args:
            list1: The list that should contain all values.
            list2: The list whose values should be found.
            msg: Optional custom error message.
            values: When true, the default error message is added at the end of
              the possible custom error message.
            ignore_case: Whether to ignore case in comparison.

        The order of values and the number of values are not taken into
        account.

        See [Lists Should Be Equal] for more information about configuring
        the error message with `msg` and `values` arguments.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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
        """Logs contents of the `list` using the given `level`.

        Args:
            list_: The list to log.
            level: The log level to use.

        !!! note
            The `list_` argument will be renamed to `list` in Robot Framework 8.0.
            Users should avoid using the named argument syntax like `list_=${mylist}`
            and pass the list positionally like `${mylist}` instead. See issue
            [#5762] for more information.
        """
        logger.write("\n".join(self._log_list(list_)), level)

    def _log_list(self, list_: Sequence) -> "Iterator[str]":
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
        """Converts the given `item` to a Python `dict` type.

        Args:
            item: The item to convert to a dictionary.

        Returns:
            The converted dictionary.

        Mainly useful for converting other mappings to normal dictionaries.
        This includes converting Robot Framework's own `DotDict` instances
        that it uses if variables are created using the `&{var}` syntax.

        Use [Create Dictionary] from the BuiltIn library for constructing new
        dictionaries.
        """
        return dict(item)  # type: ignore

    def set_to_dictionary(
        self,
        dictionary: MutableMapping,
        *key_value_pairs: object,
        **items: object,
    ) -> MutableMapping:
        """Adds the given `key_value_pairs` and/or `items` to the `dictionary`.

        Args:
            dictionary: The dictionary to modify.
            *key_value_pairs: Keys and values to add as separate arguments.
            **items: Keys and values to add using the `name=value` syntax.

        Returns:
            The modified dictionary.

        Raises:
            ValueError: If `key_value_pairs` does not contain an even number
              of arguments.

        If given items already exist in the dictionary, their values are updated.

        It is easiest to specify items using the `name=value` syntax:

        ```robotframework
        *** Test Cases ***
        `name=value` syntax
            ${dict_1} =    Copy Dictionary    ${DICT_A}
            ${expected} =    Copy Dictionary    ${DICT_A}
            Set To Dictionary    ${expected}    key=value    second=${2}
            ${updated} =    Set To Dictionary    ${dict_1}    key=value    second=${2}
            Dictionaries Should Be Equal    ${updated}    ${expected}
        ```

        A limitation of the above syntax is that keys must be strings.

        That can be avoided by passing keys and values as separate arguments:

        ```robotframework
        *** Test Cases ***
        Keys and values separately
            ${dict_1} =    Copy Dictionary    ${DICT_A}
            ${expected} =    Copy Dictionary    ${DICT_A}
            Set To Dictionary    ${expected}    key    value    ${2}    value 2
            ${updated} =    Set To Dictionary    ${dict_1}    key    value    ${2}    value 2
            Dictionaries Should Be Equal    ${updated}    ${expected}
        ```

        Starting from Robot Framework 6.1, it is also possible to use the native
        item assignment syntax. This is equivalent to the above:

        ```robotframework
        *** Test Cases ***
        Item assignment syntax
            ${dict_1} =    Copy Dictionary    ${DICT_A}
            ${expected} =    Copy Dictionary    ${DICT_A}
            Set To Dictionary    ${expected}    key    value    ${2}    value 2
            ${dict_1}[key] =    Set Variable    value
            ${dict_1}[${2}] =    Set Variable    value 2
            Dictionaries Should Be Equal    ${dict_1}    ${expected}
        ```
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
        """Removes the given `keys` from the `dictionary`.

        Args:
            dictionary: The dictionary to modify.
            *keys: Keys to remove.

        Returns:
            The modified dictionary.

        If the given `key` does not exist in the `dictionary`, it is ignored.

        Starting from Robot Framework 7.4, the modified dictionary is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Remove from dictionary
            ${dict_1} =    Copy Dictionary    ${DICT_ABC}
            ${expected} =    Copy Dictionary    ${DICT_ABC}
            Remove From Dictionary    ${expected}    b
            ${updated} =    Remove From Dictionary    ${dict_1}    b    x    y
            Dictionaries Should Be Equal    ${updated}    ${expected}
        ```
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
        """Removes the given `key` from the `dictionary` and returns its value.

        Args:
            dictionary: The dictionary to modify.
            key: The key to remove.
            default: Default value returned if the key is not found.

        Returns:
            The value of the removed key.

        The keyword fails if the given `key` cannot be found from the `dictionary`
        by default. If optional `default` value is given, it will be returned instead.

        Examples:

        ```robotframework
        *** Test Cases ***
        Pop from dictionary
            ${dict_1} =    Copy Dictionary    ${DICT_ABC}
            ${expected} =    Copy Dictionary    ${DICT_ABC}
            Remove From Dictionary    ${expected}    b
            ${val} =    Pop From Dictionary    ${dict_1}    b
            Should Be Equal    ${val}    ${2}
            Dictionaries Should Be Equal    ${dict_1}    ${expected}
        ```
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
        """Keeps the given `keys` in the `dictionary` and removes all others.

        Args:
            dictionary: The dictionary to modify.
            *keys: Keys to keep.

        Returns:
            The modified dictionary.

        If a certain key does not exist in the `dictionary`, it is ignored.

        Starting from Robot Framework 7.4, the modified dictionary is also returned.

        Examples:

        ```robotframework
        *** Test Cases ***
        Keep in dictionary
            ${dict_1} =    Copy Dictionary    ${DICT_ABCD}
            ${expected} =    Copy Dictionary    ${DICT_ABCD}
            Remove From Dictionary    ${expected}    a    c
            ${updated} =    Keep In Dictionary    ${dict_1}    b    x    d
            Dictionaries Should Be Equal    ${updated}    ${expected}
        ```
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

        Args:
            dictionary: The dictionary to copy.
            deepcopy: Whether to also copy items.

        Returns:
            A copy of the dictionary.

        By default, returns a new dictionary with same items as in the original.
        Set the `deepcopy` argument to a true value if also items should be copied.
        """
        if deepcopy:
            return copy.deepcopy(dictionary)
        return copy.copy(dictionary)

    def get_dictionary_keys(
        self,
        dictionary: Mapping,
        sort_keys: bool = True,
    ) -> "list[object]":
        """Returns keys of the given `dictionary` as a list.

        Args:
            dictionary: The dictionary to get keys from.
            sort_keys: Whether to sort keys.

        Returns:
            Dictionary keys as a list.

        By default, keys are returned in sorted order (assuming they are
        sortable), but they can be returned in the original order by giving
        `sort_keys` a false value.

        Examples:

        ```robotframework
        *** Test Cases ***
        Get dictionary keys
            ${keys} =    Get Dictionary Keys    ${DICT_ABC}
            Should Be Equal    ${keys}    ["a", "b", "c"]    type=list
        ```
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
        """Returns values of the given `dictionary` as a list.

        Args:
            dictionary: The dictionary to get values from.
            sort_keys: Whether to sort keys.

        Returns:
            Dictionary values as a list.

        Uses [Get Dictionary Keys] to get keys and then returns corresponding
        values. By default, keys are sorted and values returned in that order,
        but this can be changed by giving `sort_keys` a false value.

        Examples:

        ```robotframework
        *** Test Cases ***
        Get dictionary values
            ${values} =    Get Dictionary Values    ${DICT_ABC}
            Should Be Equal    ${values}    [1, 2, 3]    type=list
        ```
        """
        keys = self.get_dictionary_keys(dictionary, sort_keys=sort_keys)
        return [dictionary[k] for k in keys]

    def get_dictionary_items(
        self,
        dictionary: Mapping,
        sort_keys: bool = True,
    ) -> "list[tuple[object, object]]":
        """Returns items of the given `dictionary` as a list.

        Args:
            dictionary: The dictionary to get items from.
            sort_keys: Whether to sort keys.

        Returns:
            Dictionary items as a flat list.

        Uses [Get Dictionary Keys] to get keys and then returns corresponding
        items. By default, keys are sorted and items returned in that order,
        but this can be changed by giving `sort_keys` a false value.

        Items are returned as a flat list so that first item is a key,
        second item is a corresponding value, third item is the second key,
        and so on.

        Examples:

        ```robotframework
        *** Test Cases ***
        Get dictionary items
            ${items} =    Get Dictionary Items    ${DICT_ABC}
            Should Be Equal    ${items}    ["a", 1, "b", 2, "c", 3]    type=list
        ```
        """
        keys = self.get_dictionary_keys(dictionary, sort_keys=sort_keys)
        return [i for key in keys for i in (key, dictionary[key])]

    def get_from_dictionary(
        self,
        dictionary: Mapping,
        key: object,
        default: object = NOT_SET,
    ) -> object:
        """Returns a value from the given `dictionary` based on the given `key`.

        Args:
            dictionary: The dictionary to get a value from.
            key: The key whose value to get.
            default: Default value returned if the key is not found.

        Returns:
            The value of the given key.

        If the given `key` cannot be found from the `dictionary`, this
        keyword fails. If optional `default` value is given, it will be
        returned instead of failing.

        Examples:

        ```robotframework
        *** Test Cases ***
        Get from dictionary
            ${value} =    Get From Dictionary    ${DICT_ABC}    b
            Should Be Equal    ${value}    ${2}
        ```

        Support for `default` is new in Robot Framework 6.0.
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
        """Fails if `key` is not found from `dictionary`.

        Args:
            dictionary: The dictionary to verify.
            key: The key that should be found.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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
        """Fails if `key` is found from `dictionary`.

        Args:
            dictionary: The dictionary to verify.
            key: The key that should not be found.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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
        """Fails is item `key` does not exist and have value `value`.

        Args:
            dictionary: The dictionary to verify.
            key: The item to search for.
            value: The expected value.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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
        """Fails if `value` is not found from `dictionary`.

        Args:
            dictionary: The dictionary to verify.
            value: The value that should be found.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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
        """Fails if `value` is found from `dictionary`.

        Args:
            dictionary: The dictionary to verify.
            value: The value that should not be found.
            msg: Optional custom error message.
            ignore_case: Whether to ignore case in comparison.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
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

        Args:
            dict1: The first dictionary.
            dict2: The second dictionary.
            msg: Optional custom error message.
            values: Controls whether default differences are included in the error message.
            ignore_keys: Keys to ignore in the comparison.
            ignore_case: Whether to ignore case in comparison.
            ignore_value_order: Whether to ignore order in list-like values.

        First the equality of dictionaries' keys is checked and after that all
        the key value pairs. If there are differences between the values, those
        are listed in the error message. The types of the dictionaries do not
        need to be same.

        `ignore_keys` can be used to provide a list of keys to ignore in the
        comparison. This option is new in Robot Framework 6.1. It works recursively
        with nested dictionaries starting from Robot Framework 7.0.

        Examples:

        ```robotframework
        *** Variables ***
        &{DICT1}         first=same    second=different case
        &{DICT2}         first=same
        &{DICT3}         first=same    second=DIFFERENT CASE

        *** Test Cases ***
        Comparison fails with different items
            Dictionaries Should Be Equal    ${DICT1}    ${DICT2}

        Comparison fails with different values
            Dictionaries Should Be Equal    ${DICT1}    ${DICT3}

        Comparison when ignoring case
            Dictionaries Should Be Equal    ${DICT1}    ${DICT3}    ignore_case=True

        Comparison when ignoring keys
            VAR    @{ignore}    second
            Dictionaries Should Be Equal    ${DICT1}    ${DICT2}    ignore_keys=${ignore}
            Dictionaries Should Be Equal    ${DICT1}    ${DICT3}    ignore_keys=${ignore}
        ```

        See [Lists Should Be Equal] for more information about configuring
        the error message with `msg` and `values` arguments.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
        Robot Framework 7.0.

        The `ignore_value_order` argument can be used to make comparison in case of
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
        """Fails unless all items in `dict2` are found from `dict1`.

        Args:
            dict1: The dictionary that should contain all items.
            dict2: The dictionary whose items should be found.
            msg: Optional custom error message.
            values: Controls whether default differences are included in the error message.
            ignore_case: Whether to ignore case in comparison.
            ignore_value_order: Whether to ignore order in list-like values.

        See [Lists Should Be Equal] for more information about configuring
        the error message with `msg` and `values` arguments.

        The `ignore_case` argument can be used to make comparison case-insensitive.
        See the [Ignore case] section for more details. This option is new in
        Robot Framework 7.0.

        The `ignore_value_order` argument can be used to make comparison in case of
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
        """Logs the contents of the `dictionary` using the given `level`.

        Args:
            dictionary: The dictionary to log.
            level: The log level to use.
        """
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

    `Collections` is Robot Framework's standard library that provides a
    set of keywords for handling Python lists and dictionaries. This
    library has keywords, for example, for modifying and getting
    values from lists and dictionaries (e.g. [Append To List],
    [Get From Dictionary]) and for verifying their contents (e.g.
    [Lists Should Be Equal], [Dictionary Should Contain Value]).

    ### Table of contents

    %TOC%

    # Related keywords in BuiltIn

    Following keywords in the [BuiltIn] library can also be used with
    lists and dictionaries:

    |         Keyword Name         | Applicable With |
    | ---------------------------- | --------------- |
    | `Create List`                | lists           |
    | `Create Dictionary`          | dicts           |
    | `Get Length`                 | both            |
    | `Length Should Be`           | both            |
    | `Should Be Empty`            | both            |
    | `Should Not Be Empty`        | both            |
    | `Should Contain`             | both            |
    | `Should Not Contain`         | both            |
    | `Should Contain X Times`     | lists           |
    | `Should Not Contain X Times` | lists           |
    | `Get Count`                  | lists           |

    # Using with list-like and dictionary-like objects

    List related keywords can in general be used with tuples and other sequences,
    not only with `list` objects. List keywords that validate something typically
    even work with sets and mappings (with mappings they look only at keys).
    If keywords that modify lists are used with immutable sequences such as tuples,
    values are automatically converted to lists. In such cases the original value
    obviously is not mutated, but these keywords also return the modified value
    and that can be used instead.

    Dictionary related keywords also generally work with any mapping, not only
    with `dict` objects. If keywords that modify dictionaries are used with
    immutable mappings, values are automatically converted to dictionaries.
    Original values cannot be modified in these cases either, but modified values
    are returned and can be used instead.

    What values each keyword actually accepts can be seen from argument types
    and keyword documentation.

    Returning values from keywords that modify lists or dictionaries is new
    in Robot Framework 7.4. With earlier version these keywords could only
    be used with mutable values.

    # Ignore case

    Various keywords support ignoring case in comparisons by using the optional
    `ignore_case` argument. Case-insensitivity can be enabled by using
    `ignore_case=True` and it works recursively.

    With dictionaries, it is also possible to use special values `KEYS` and
    `VALUES` to normalize only keys or values, respectively. These options
    themselves are case-insensitive and also singular forms `KEY` and
    `VALUE` are supported.

    If a dictionary contains keys that normalize to the same value, e.g.
    `{'a': 1, 'A': 2}`, normalizing keys causes an error.

    Examples:

    ```robotframework
    *** Test Cases ***
    Ignore case
        VAR    @{list1}    abc    DEF
        VAR    @{list2}    ABC    def
        VAR    &{dict1}    key=value
        VAR    &{dict2}    key=VALUE
        Lists Should Be Equal    ${list1}    ${list2}    ignore_case=True
        Dictionaries Should Be Equal    ${dict1}    ${dict2}    ignore_case=VALUES
    ```

    Notice that some keywords accept also an older `case_insensitive` argument
    in addition to `ignore_case`. The latter is new in Robot Framework 7.0 and
    should be used unless there is a need to support older versions. The old
    argument is considered deprecated and will eventually be removed.

    Starting from Robot Framework 7.4, case-insensitivity works also with
    bytes, not only with strings.

    # Variables in examples

    The following shared variables are used in examples throughout this
    documentation to keep test data consistent and easy to read.

    ```robotframework
    *** Variables ***
    @{LIST_ABC}      a    b    c
    @{LIST_ABCDE}    a    b    c    d    e

    &{DICT_A}        a=${1}
    &{DICT_ABC}      b=${2}    a=${1}    c=${3}
    &{DICT_ABCD}     a=${1}    b=${2}    c=${3}    d=${4}
    ```

    <!---  Markdown comment to hide library import that eases testing examples.
           Can be removed if a separate example with the import is added.

    ```robotframework
    *** Settings ***
    Library          Collections
    ```
    --->

    [BuiltIn]: https://robotframework.org/robotframework/latest/libraries/BuiltIn.html
    [#5762]: https://github.com/robotframework/robotframework/issues/5762
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = get_version()
    ROBOT_LIBRARY_DOC_FORMAT = "Markdown"

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
        r"""Fails if `pattern` is not found in `list`.

        Args:
            list: The list to search.
            pattern: The pattern to match.
            msg: Optional custom error message.
            case_insensitive: Deprecated. Use `ignore_case` instead.
            whitespace_insensitive: Deprecated. Use `ignore_whitespace` instead.
            ignore_case: Whether to ignore case when matching.
            ignore_whitespace: Whether to ignore whitespace when matching.

        By default, pattern matching is similar to matching files in a shell
        and is case-sensitive and whitespace-sensitive. In the pattern syntax,
        `*` matches to anything and `?` matches to any single character. You
        can also prepend `glob=` to your pattern to explicitly use this pattern
        matching behavior.

        If you prepend `regexp=` to your pattern, the pattern is considered to
        be a regular expression that uses Python's
        [regular expression syntax](http://docs.python.org/library/re.html).
        Notice that the backslash character often used with regular
        expressions is an escape character in Robot Framework data and needs
        to be escaped with another backslash like `regexp=\\d{6}`. See the
        [BuiltIn] keyword `Should Match Regexp` for more details.

        Matching is case-sensitive by default, but that can be changed by giving
        the `ignore_case` argument a true value.
        This argument is new in Robot Framework 7.0, but with earlier versions
        it is possible to use `case_insensitive` for the same purpose.

        It is possible to ignore all whitespace by giving the `ignore_whitespace`
        argument a true value. This argument is new in Robot Framework 7.0 as well,
        and with earlier versions it is possible to use `whitespace_insensitive`.

        Notice that both `case_insensitive` and `whitespace_insensitive`
        are considered deprecated. They will eventually be removed.

        Non-string values in lists are ignored when matching patterns.

        Examples:

        ```robotframework
        *** Variables ***
        @{LIST}          foo    bar    abc 123

        *** Test Cases ***
        Match using glob pattern
            Should Contain Match    ${LIST}    f*
            Should Contain Match    ${LIST}    b?r
            Should Contain Match    ${LIST}    abc [1-9][1-9][1-9]

        Match using regexp
            Should Contain Match    ${LIST}    regexp=f.*
            Should Contain Match    ${LIST}    regexp=b.r
            Should Contain Match    ${LIST}    regexp=abc \\d\\d\\d

        Normalization
            Should Contain Match    ${LIST}    ABC *     ignore_case=True
            Should Contain Match    ${LIST}    abc???    ignore_whitespace=True
        ```
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
        """Fails if `pattern` is found in `list`.

        Args:
            list: The list to search.
            pattern: The pattern that should not match.
            msg: Optional custom error message.
            case_insensitive: Deprecated. Use `ignore_case` instead.
            whitespace_insensitive: Deprecated. Use `ignore_whitespace` instead.
            ignore_case: Whether to ignore case when matching.
            ignore_whitespace: Whether to ignore whitespace when matching.

        Exact opposite of [Should Contain Match] keyword. See that keyword
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
        """Returns a list of matches to `pattern` in `list`.

        Args:
            list: The list to search.
            pattern: The pattern to match.
            case_insensitive: Deprecated. Use `ignore_case` instead.
            whitespace_insensitive: Deprecated. Use `ignore_whitespace` instead.
            ignore_case: Whether to ignore case when matching.
            ignore_whitespace: Whether to ignore whitespace when matching.

        Returns:
            A list containing matching items.

        For more information on `pattern`, `case_insensitive/ignore_case`, and
        `whitespace_insensitive/ignore_whitespace`, see [Should Contain Match].

        Examples:

        ```robotframework
        *** Variables ***
        @{LIST}          foo    bar    abc 123

        *** Test Cases ***
        Get matches
            ${matches} =    Get Matches    ${LIST}    *A*    ignore_case=True
            Should Be Equal    ${matches}    ["bar", "abc 123"]    type=list

        Get no matches
            ${matches} =    Get Matches    ${LIST}    no match
            Should Be Empty    ${matches}
        ```
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
        """Returns the count of matches to `pattern` in `list`.

        Args:
            list: The list to search matches from.
            pattern: The pattern to match.
            case_insensitive: Deprecated. Use `ignore_case` instead.
            whitespace_insensitive: Deprecated. Use `ignore_whitespace` instead.
            ignore_case: Whether to ignore case when matching.
            ignore_whitespace: Whether to ignore whitespace when matching.

        Returns:
            The number of matches.

        For more information on `pattern`, `case_insensitive/ignore_case`, and
        `whitespace_insensitive/ignore_whitespace`, see [Should Contain Match].

        Examples:

        ```robotframework
        *** Variables ***
        @{LIST}          foo    bar    abc 123

        *** Test Cases ***
        Get match count
            ${matches} =    Get Match Count    ${LIST}    *A*    ignore_case=True
            Should Be Equal    ${matches}    2    type=int

        Get zero match count
            ${matches} =    Get Match Count    ${LIST}    no match
            Should Be Equal    ${matches}    0    type=int
        ```
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
        sequence: ListLike,
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
