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

from typing import Generic, Literal, overload, TypeVar, TYPE_CHECKING

from robot.utils import NormalizedDict, plural_or_not as s, seq2str

from .keywordimplementation import KeywordImplementation

if TYPE_CHECKING:
    from .testlibraries import TestLibrary
    from .resourcemodel import ResourceFile


K = TypeVar('K', bound=KeywordImplementation)


class KeywordFinder(Generic[K]):

    def __init__(self, owner: 'TestLibrary|ResourceFile'):
        self.owner = owner
        self.cache: KeywordCache|None = None

    @overload
    def find(self, name: str, count: Literal[1]) -> 'K':
        ...

    @overload
    def find(self, name: str, count: 'int|None' = None) -> 'list[K]':
        ...

    def find(self, name: str, count: 'int|None' = None) -> 'list[K]|K':
        """Find keywords based on the given ``name``.

        With normal keywords matching is a case, space and underscore insensitive
        string comparison and there cannot be more than one match. With keywords
        accepting embedded arguments, matching is done against the name and
        there can be multiple matches.

        Returns matching keywords as a list, possibly as an empty list, without
        any validation by default. If the optional ``count`` is used, raises
        a ``ValueError`` if the number of found keywords does not match. If
        ``count`` is ``1`` and exactly one keyword is found, returns that keyword
        directly and not as a list.
        """
        if self.cache is None:
            self.cache = KeywordCache[K](self.owner.keywords)
        return self.cache.find(name, count)

    def invalidate_cache(self):
        self.cache = None


class KeywordCache(Generic[K]):

    def __init__(self, keywords: 'list[K]'):
        self.normal = NormalizedDict[K](ignore='_')
        self.embedded: list[K] = []
        add_normal = self.normal.__setitem__
        add_embedded = self.embedded.append
        for kw in keywords:
            if kw.embedded:
                add_embedded(kw)
            else:
                add_normal(kw.name, kw)

    def find(self, name: str, count: 'int|None' = None) -> 'list[K]|K':
        try:
            keywords = [self.normal[name]]
        except KeyError:
            keywords = [kw for kw in self.embedded if kw.matches(name)]
        if count is not None:
            if len(keywords) != count:
                names = ': ' + seq2str([kw.name for kw in keywords]) if keywords else '.'
                raise ValueError(f"Expected {count} keyword{s(count)} matching name "
                                 f"'{name}', found {len(keywords)}{names}")
            if count == 1:
                return keywords[0]
        return keywords
